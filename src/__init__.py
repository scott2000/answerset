# MIT License
#
# Copyright (c) 2023 Scott Taylor
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import difflib
import html
import unicodedata as ucd
import re
from typing import Iterator, Optional

try:
    import aqt
    config = aqt.mw.addonManager.getConfig(__name__)
except:
    config = None

def get_config_var(var_name, default_value):
    try:
        value = config[var_name]
    except:
        return default_value

    if type(value) is not type(default_value):
        return default_value

    return value

config_answer_choice_comments = get_config_var('Enable Answer Choice Comments [...]', False)
config_answer_comments = get_config_var('Enable Answer Comments (...)', False)
config_lenient_validation = get_config_var('Enable Lenient Validation', True)
config_ignore_separators_in_brackets = get_config_var('Ignore Separators in Brackets', True)
config_ignored_characters = get_config_var('Ignored Characters', ' .-')

space_re = re.compile(r" +")
prefix_limit = 3
max_similarity = 0x7fffffff

bracket_start = '(['
bracket_end = ')]'
bracket_chars = bracket_start + bracket_end
whitespace_chars = ' \t\r\n'
keep_in_alternative_chars = whitespace_chars + bracket_chars
junk_chars = config_ignored_characters.replace(' ', whitespace_chars) + bracket_chars
junk_trans = {ord(ch): None for ch in junk_chars}

def similarity(a: str, b: str):
    """
    Returns the length of the longest common subsequence between two strings suffixes.
    """

    # Make string "b" be smaller than "a"
    if len(a) < len(b):
        a, b = b, a

    # If "b" is empty, the similarity is zero
    if not len(b):
        return 0

    # Iteratively compute using an array and two variables
    arr = [0] * len(b)
    for i in range(len(a)):
        prev_prev = 0
        curr_prev = 0

        for j in range(len(b)):
            prev_curr = arr[j]

            if a[i] == b[j]:
                arr[j] = prev_prev + 1
            else:
                arr[j] = max(prev_curr, curr_prev, prev_prev)

            prev_prev = prev_curr
            curr_prev = arr[j]

    return arr[-1]

def adj_similarity(a_full: str, b_full: str):
    """
    Returns the similarity between two strings adjusted to prefer matching
    prefixes and ignore junk characters.
    """

    # Remove characters that aren't useful for matching
    a = a_full.translate(junk_trans)
    b = b_full.translate(junk_trans)

    # If a string has all junk characters, then leave them
    if not a or not b:
        a, b = a_full, b_full

    # If equal, then return max_similarity immediately
    if a == b:
        return max_similarity

    # Find the length of the shared prefix, up to prefix_limit
    overlap = min(len(a), len(b), prefix_limit)
    prefix = 0
    while prefix < overlap and a[prefix] == b[prefix]:
        prefix += 1

    # Return similarity adjusted for prefix length
    return prefix_limit * similarity(a, b) + prefix

class Arranger:
    def __init__(self, given, correct):
        self.given = given
        self.correct = correct
        self.memo = {}
        self.closest = {}
        self.assigned = {}
        self.used = set()

    def get_similarity(self, i, j):
        """Find the similarity between a "given" part and a "correct" part."""

        if (i, j) in self.memo:
            return self.memo[(i, j)]

        s = adj_similarity(self.given[i][0], self.correct[j][0])
        self.memo[(i, j)] = s
        return s

    def max_for(self, i):
        """
        Compute the maximum similarity for a specific "given" part to the nearest
        matching "correct" part.
        """

        # Check for already computed maximum similarity
        if i in self.closest and self.closest[i] not in self.used:
            return self.get_similarity(i, self.closest[i])

        # Find the closest "correct" part
        closest = None
        closest_similarity = -1
        for j in range(len(self.correct)):
            # Skip "correct" parts which were already used
            if j in self.used:
                continue

            # Update maximum similarity
            s = self.get_similarity(i, j)
            if s > closest_similarity:
                closest = j
                closest_similarity = s

                # A similarity of max_similarity is an exact match
                if s == max_similarity:
                    break

        # Remember the closest value and return the similarity
        self.closest[i] = closest
        return closest_similarity

    def step(self):
        """
        Make an assignment for the most similar pair. Returns True if more
        steps are needed and False otherwise.
        """

        # If all "given" parts are assigned, we are done
        if len(self.assigned) == len(self.given):
            return False

        # If all "correct" parts are used, we are done
        if len(self.used) == len(self.correct):
            return False

        # Find closest pair of "given" and "correct"
        closest = None
        closest_similarity = -1
        for i in range(len(self.given)):
            # Skip "given" parts which are already assigned
            if i in self.assigned:
                continue

            # Update maximum similarity
            s = self.max_for(i)
            if s > closest_similarity:
                closest = i
                closest_similarity = s

                # A similarity of max_similarity is an exact match
                if s == max_similarity:
                    break

        # Record the assignment
        target = self.closest[closest]
        self.assigned[closest] = target
        self.used.add(target)

        return True

    def finalize(self):
        """Create a list of parts which should be compared."""

        # Put "given" parts and their matching "correct" parts first
        parts = []
        for i in range(len(self.given)):
            if i in self.assigned:
                parts.append((self.given[i], self.correct[self.assigned[i]]))
            else:
                parts.append((self.given[i], None))

        # Put all unused "correct" parts after
        for j in range(len(self.correct)):
            if j not in self.used:
                parts.append((None, self.correct[j]))

        return parts

def arrange(given, correct):
    """Rearrange parts so that similar ones line up."""

    arranger = Arranger(given, correct)
    while arranger.step():
        pass
    return arranger.finalize()

def split_comment(string: str, start: str, end: str, enabled: bool) -> tuple[str, str]:
    """
    Find a comment delimited by "start" and "end" and remove it from the end of
    the string. The comment cannot be the whole string, and it must come at the
    end. Nesting is allowed, but not multiple independent comments in a string.
    """

    # If disabled by config, don't try to split
    if not enabled:
        return string, ''

    # If the string is too small or doesn't end with the delimiter, don't split
    if len(string) < 3 or string[-1] != end:
        return string, ''

    # Iterate backwards through string checking for delimiters
    depth = 1
    for i in range(2, len(string)):
        ch = string[-i]
        if ch == start:
            depth -= 1

            # If start of comment is found, make sure it is valid
            if depth == 0:
                stripped = string[:-i].strip()

                # If the remaining string is empty, it's invalid
                if not stripped:
                    break

                # If there are delimiters in the remaining string, it's invalid
                if start in stripped or end in stripped:
                    break

                # If there is no space before the start of the comment, it's invalid
                if string[-(i + 1)] != ' ':
                    break

                # It is valid so return the comment separately
                return stripped, ' ' + string[-i:]

        elif ch == end:
            depth += 1

    return string, ''

def find_outer_bracket_ranges(input: Iterator[str], lenient: bool = False) -> list[tuple[int, int]]:
    found_ranges = []
    expected_ends = []
    for i, ch in enumerate(input):
        if ch == '(':
            expected_ends.append((i, ')'))
        elif ch == '[':
            expected_ends.append((i, ']'))
        elif ch == ')' or ch == ']':
            try:
                start_index, end_char = expected_ends.pop()
            except IndexError:
                if not lenient:
                    return []

                continue

            if end_char != ch:
                return []

            if not expected_ends:
                found_ranges.append((start_index, i + 1))

    if expected_ends and not lenient:
        return []

    return found_ranges

def index_in_any_range(index: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= index < end for start, end in ranges)

def find_indices(haystack: str, needle: str, ranges: list[tuple[int, int]]) -> Iterator[int]:
    return (i for i, ch in enumerate(haystack) if ch == needle and not index_in_any_range(i, ranges))

def has_separator(string: str, sep: str, bracket_ranges: list[tuple[int, int]]) -> bool:
    return any(True for _ in find_indices(string, sep, bracket_ranges))

def split_except_for_ranges(string: str, sep: str, ranges: list[tuple[int, int]]) -> list[str]:
    sep_indices = list(find_indices(string, sep, ranges))

    if not sep_indices:
        return [string]

    parts = []
    last = 0
    for i in sep_indices:
        parts.append(string[last:i])
        last = i + 1

    parts.append(string[last:])
    return parts

def split_options(string: str, sep: str, bracket_ranges: list[tuple[int, int]]) -> list[tuple[str, str]]:
    """
    Split a string on a separator, trim whitespace, and remove a comment
    delimited by square brackets.
    """

    stripped = []
    for part in split_except_for_ranges(string, sep, bracket_ranges):
        s = part.strip()
        if s:
            stripped.append(split_comment(s, '[', ']', config_answer_choice_comments))

    return stripped

def is_combining(ch: str) -> bool:
    """Check if a character is a Unicode combining mark."""

    return ucd.category(ch).startswith('M')

def group_combining(string: str) -> list[str]:
    """Group combining characters with the previous character."""

    parts = []
    current = ''
    for ch in string:
        if is_combining(ch):
            if not current:
                current = '\xa0'

            current += ch
        else:
            if current:
                parts.append(current)

            current = ch

    if current:
        parts.append(current)

    return parts

def is_junk(ch: str):
    return len(ch) == 1 and ord(ch) in junk_trans

def good(s: str) -> str:
    return f"<span class=typeGood>{html.escape(s)}</span>"

def bad(s: str) -> str:
    return f"<span class=typeBad>{html.escape(s)}</span>"

def missed(s: str) -> str:
    return f"<span class=typeMissed>{html.escape(s)}</span>"

def not_code(s: str) -> str:
    return f"</code>{s}<code id=typeans>"

def find_potential_alternative_end(segment: list[str], bracket_start_chars: str, bracket_end_chars: str, alpha_after: bool) -> Optional[int]:
    """
    Find the end of a missing alternative which starts with a slash.
    Alternatives should end at the first space, unless inside of brackets.
    If there are no spaces or brackets, then the alternative is the entire
    segment, in which case it must not be followed by an alpha character.
    Slashes inside the alternative must be followed by alpha characters.
    """

    end = None
    require_alpha = False

    for i, ch in enumerate(segment):
        if require_alpha and not ch.isalpha():
            return None

        require_alpha = ch == '/'

        if ch in bracket_start_chars:
            if ch is None:
                end = i
            break

        if ch in bracket_end_chars:
            end = i + 1
            break

        if end is None and ch in whitespace_chars:
            end = i

    if require_alpha:
        return None

    if end is None and not alpha_after:
        return len(segment)

    return end

def remove_alternative(segment: list[str], alpha_before: bool, alpha_after: bool) -> bool:
    """
    Remove an alternative from the start/end of a segment. An alternative is
    a series of single words separated by slashes, which allows the user to
    pick any one of the words. If a missing segment is part of an alternative,
    no error should be reported.
    """

    if alpha_before and segment and segment[0] == '/':
        end = find_potential_alternative_end(segment, bracket_start, bracket_end, alpha_after)
        if end is not None:
            segment = segment[end:]

    if alpha_after and segment and segment[-1] == '/':
        # Use the same method, but reverse the segment first to search from the end backwards
        rev_end = find_potential_alternative_end(segment[::-1], bracket_end, bracket_start, alpha_before)
        if rev_end is not None:
            segment = segment[:-rev_end]

    return segment

def remove_bracketed_text(segment: list[str]) -> list[str]:
    """Remove all bracketed text from a segment."""

    result = []
    last_end = 0
    for start, end in find_outer_bracket_ranges(segment, lenient=True):
        result.extend(segment[last_end:start])
        last_end = end

    result.extend(segment[last_end:])

    return result

def is_missing_allowed(segment: list[str], alpha_before: bool, alpha_after: bool) -> bool:
    """
    Check whether a segment of text is allowed to be missing. If it is allowed
    to be missing, then it will not be reported as incorrect if it is missing.
    Otherwise, it will be shown as incorrect if it is missing.
    """

    # Missing text is only allowed if lenient validation is enabled
    if not config_lenient_validation:
        return False

    # Remove any alternatives, since they are allowed to be missing
    segment = remove_alternative(segment, alpha_before, alpha_after)

    # Remove bracketed text, since it is allowed to be missing
    segment = remove_bracketed_text(segment)

    # If the remainder is all junk, it is allowed to be missing
    return all(is_junk(ch) for ch in segment)

def isalpha_at_index(s: list[str], i: int) -> bool:
    return 0 <= i < len(s) and s[i].isalpha()

def render_diffs(given, correct, given_elems, correct_elems):
    """Create the diff comparison strings for each part."""

    # Separate comments from parts
    given, given_comment = given
    correct, correct_comment = correct

    # Only diff comments if they were given
    if given_comment:
        given += given_comment
        correct += correct_comment

    # Group combining characters to give cleaner diffs
    given = group_combining(given)
    correct = group_combining(correct)

    has_error = False
    given_elem = ''
    correct_elem = ''

    given_index = 0
    correct_index = 0

    # Iterate through matching blocks to render the diff
    s = difflib.SequenceMatcher(None, given, correct, autojunk=False)
    for i, j, cnt in s.get_matching_blocks():
        # Check for bad text in "given"
        if given_index < i:
            has_error = True
            given_elem += bad(''.join(given[given_index:i]))

        # Check for missing text in "correct"
        if correct_index < j:
            correct_elem += missed(''.join(correct[correct_index:j]))

            # If completely missing in "given", add hyphen
            if given_index == i:
                alpha_before = isalpha_at_index(correct, correct_index - 1)
                alpha_after = isalpha_at_index(correct, j)

                # Check if should be ignored with lenient validation
                if not is_missing_allowed(correct[correct_index:j], alpha_before, alpha_after):
                    has_error = True
                    given_elem += bad('-')

        if not cnt:
            continue

        given_index = i + cnt
        correct_index = j + cnt

        # Add good text for both
        given_elem += good(''.join(given[i:given_index]))
        correct_elem += good(''.join(correct[j:correct_index]))

    # If a comment wasn't diffed, add it back
    if correct_comment and not given_comment:
        correct_elem += not_code(html.escape(correct_comment))

    # Append the diffs to the arrays
    given_elems.append(given_elem)
    correct_elems.append(correct_elem)

    # Return whether there was any error or not
    return has_error

def compare_answer_no_html(correct: str, given: str) -> str:
    """Display the corrections for a type-in answer."""

    # Replace consecutive spaces with a single space
    given = space_re.sub(' ', given)
    correct = space_re.sub(' ', correct)

    # Normalize using NFC to make comparison consistent
    given = ucd.normalize('NFC', given)
    correct = ucd.normalize('NFC', correct)

    # Remove comments in parentheses
    correct, correct_comment = split_comment(correct, '(', ')', config_answer_comments)

    # Only separate comment for given if present for correct
    if correct_comment:
        given, given_comment = split_comment(given, '(', ')', config_answer_comments)
    else:
        given_comment = ''

    # Find bracket ranges in both answers (if config option enabled)
    if config_ignore_separators_in_brackets:
        correct_bracket_ranges = find_outer_bracket_ranges(correct)
        given_bracket_ranges = find_outer_bracket_ranges(given)
    else:
        correct_bracket_ranges = []
        given_bracket_ranges = []

    # Pick separator as ';' if one is used, otherwise ','
    if has_separator(correct, ';', correct_bracket_ranges):
        sep = ';'
    else:
        sep = ','

    # Split on the separator
    correct = split_options(correct, sep, correct_bracket_ranges)
    given = split_options(given, sep, given_bracket_ranges)

    # Arrange the parts so that similar ones line up and render the diffs
    has_error = False
    given_elems = []
    correct_elems = []
    for given, correct in arrange(given, correct):
        if not given:
            correct_elems.append(missed(correct[0]) + correct[1])
        elif not correct:
            has_error = True
            given_elems.append(bad(''.join(given)))
        else:
            has_error |= render_diffs(given, correct, given_elems, correct_elems)

    # Diff comments if they were given
    if given_comment:
        given = given_comment.strip()
        correct = correct_comment.strip()
        has_error |= render_diffs(
                (given, ''), (correct, ''), given_elems, correct_elems)

    sep = not_code(html.escape(sep) + ' ')
    res = '<div><code id=typeans>'

    # Only show the given part if there was an error
    if has_error:
        # Combine the diffs for all "given" parts
        start = True
        for elem in given_elems:
            if start:
                start = False
            else:
                res += sep
            res += elem

        res += '<br><span id=typearrow>&darr;</span><br>'

    # Combine the diffs for all "correct" parts
    start = True
    for elem in correct_elems:
        if start:
            start = False
        else:
            res += sep
        res += elem

    # If a comment wasn't diffed, add it back
    if correct_comment and not given_comment:
        res += not_code(html.escape(correct_comment))

    res += '</code></div>'

    return res

# Up to Anki 2.1.54
try:
    from aqt.reviewer import Reviewer

    def correct(self, given: str, correct: str, **kwargs) -> str:
        return compare_answer_no_html(correct, given)

    Reviewer.correct = correct
except:
    pass

# Anki 2.1.56+ (correction was moved to Rust backend)
try:
    import aqt
    from anki.collection import Collection
    from anki.utils import html_to_text_line

    def compare_answer(self, correct: str, given: str) -> str:
        # Strip AV tags if possible
        try:
            correct = aqt.mw.col.media.strip_av_tags(correct)
        except:
            pass

        # Strip HTML tags
        correct = html_to_text_line(correct)

        return compare_answer_no_html(correct, given)

    Collection.compare_answer = compare_answer
except:
    pass
