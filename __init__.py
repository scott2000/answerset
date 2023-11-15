import difflib
import html
import unicodedata as ucd
import re

import aqt
from aqt.reviewer import Reviewer
from anki.collection import Collection
from anki.utils import html_to_text_line

space_re = re.compile(r" +")
junk_re = re.compile(r"[-\s]")
prefix_limit = 3
max_dist = 0x7fffffff

def dist(a, b):
    """Returns the Levenshtein distance between two strings suffixes."""

    # Make string "b" be smaller than "a"
    if len(a) < len(b):
        a, b = b, a

    # If "b" is empty, the distance is the length of "a"
    if not len(b):
        return len(a)

    # Iteratively compute using an array and two variables
    arr = list(range(1, len(b) + 1))
    for i in range(len(a)):
        prev_prev = i
        curr_prev = i + 1

        for j in range(len(b)):
            prev_curr = arr[j]

            if a[i] == b[j]:
                arr[j] = prev_prev
            else:
                arr[j] = min(prev_curr, curr_prev, prev_prev) + 1

            prev_prev = prev_curr
            curr_prev = arr[j]

    return arr[-1]

def adj_dist(a, b):
    """
    Returns the Levenshtein distance between two strings adjusted to prefer
    matching prefixes and ignore whitespace and hyphens.
    """

    # Remove whitespace and hyphens
    a = re.sub(junk_re, '', a)
    b = re.sub(junk_re, '', b)

    # If equal, then return 0 immediately
    if a == b:
        return 0

    # Find the length of the shared prefix
    overlap = min(len(a), len(b))
    prefix = 0
    while prefix < overlap and a[prefix] == b[prefix]:
        prefix += 1

    # Drop shared prefix for distance calculation
    a = a[prefix:]
    b = b[prefix:]

    # Return distance adjusted for prefix length
    return dist(a, b) + (prefix_limit - min(prefix, prefix_limit))

class Arranger:
    def __init__(self, given, correct):
        self.given = given
        self.correct = correct
        self.memo = {}
        self.closest = {}
        self.assigned = {}
        self.used = set()

    def get_dist(self, i, j):
        """Find the distance between a "given" part and a "correct" part."""

        if (i, j) in self.memo:
            return self.memo[(i, j)]

        d = adj_dist(self.given[i][0], self.correct[j][0])
        self.memo[(i, j)] = d
        return d

    def min_for(self, i):
        """
        Compute the minimum distance for a specific "given" part to the nearest
        matching "correct" part.
        """

        # Check for already computed minimum distance
        if i in self.closest and self.closest[i] not in self.used:
            return self.get_dist(i, self.closest[i])

        # Find the closest "correct" part
        closest = None
        closest_dist = max_dist
        for j in range(len(self.correct)):
            # Skip "correct" parts which were already used
            if j in self.used:
                continue

            # Update minimum distance
            d = self.get_dist(i, j)
            if d < closest_dist:
                closest = j
                closest_dist = d

                # A distance of 0 is an exact match
                if d == 0:
                    break

        # Remember the closest value and return the distance
        self.closest[i] = closest
        return closest_dist

    def step(self):
        """
        Make an assignment for the shortest distance pair. Returns True if more
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
        closest_dist = max_dist
        for i in range(len(self.given)):
            # Skip "given" parts which are already assigned
            if i in self.assigned:
                continue

            # Update minimum distance
            d = self.min_for(i)
            if d < closest_dist:
                closest = i
                closest_dist = d

                # A distance of 0 is an exact match
                if d == 0:
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

def split_comment(string: str, start: str, end: str) -> tuple[str, str]:
    """
    Find a comment delimited by "start" and "end" and remove it from the end of
    the string. The comment cannot be the whole string, and it must come at the
    end. Nesting is allowed, but not multiple independent comments in a string.
    """

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

def split_options(string: str, sep: str) -> list[tuple[str, str]]:
    """
    Split a string on a separator, trim whitespace, and remove a comment
    delimited by square brackets.
    """

    parts = string.split(sep)
    stripped = []
    for i in range(len(parts)):
        s = parts[i].strip()
        if s:
            stripped.append(split_comment(s, '[', ']'))

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
    return len(ch) == 1 and re.match(junk_re, ch)

def good(s: str) -> str:
    return f"<span class=typeGood>{html.escape(s)}</span>"

def bad(s: str) -> str:
    return f"<span class=typeBad>{html.escape(s)}</span>"

def missed(s: str) -> str:
    return f"<span class=typeMissed>{html.escape(s)}</span>"

def not_code(s: str) -> str:
    return f"</code>{s}<code id=typeans>"

def is_missing_alternative(segment: list[str], alphaBefore: bool, alphaAfter: bool) -> bool:
    """
    Check if a missing segment is part of an alternative. An alternative is
    a series of single words separated by slashes, which allows the user to
    pick any one of the words. If a missing segment is part of an alternative,
    no error should be reported.
    """

    if not segment:
        return False

    first, last = segment[0], segment[-1]

    # Missing alternative segment must start or end with '/'
    if first != '/' and last != '/':
        return False

    # There can be no spaces inside the alternative
    if ' ' in segment:
        return False

    # First character must be either '/' or alphabetic
    if first != '/' and not first.isalpha():
        return False

    # Last character must be either '/' or alphabetic
    if last != '/' and not last.isalpha():
        return False

    expectAlphaBefore = first == '/'
    expectAlphaAfter = last == '/'

    # There should be an alphabetic character only next to slashes
    return alphaBefore == expectAlphaBefore and alphaAfter == expectAlphaAfter

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
    s = difflib.SequenceMatcher(is_junk, given, correct, autojunk=False)
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
                alphaBefore = isalpha_at_index(correct, correct_index - 1)
                alphaAfter = isalpha_at_index(correct, j)

                # Only mark an error if it isn't a missing alternative
                if not is_missing_alternative(correct[correct_index:j], alphaBefore, alphaAfter):
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
    correct, correct_comment = split_comment(correct, '(', ')')

    # Only separate comment for given if present for correct
    if correct_comment:
        given, given_comment = split_comment(given, '(', ')')
    else:
        given_comment = ''

    # Pick separator as ';' if one is used, otherwise ','
    sep = ';' if ';' in correct else ','

    # Split on the separator
    given = split_options(given, sep)
    correct = split_options(correct, sep)

    # Arrange the parts so that similar ones line up and render the diffs
    has_error = False
    given_elems = []
    correct_elems = []
    for given, correct in Arranger.arrange(given, correct):
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

def correct(self, given: str, correct: str, **kwargs) -> str:
    return compare_answer_no_html(correct, given)

def compare_answer(self, correct: str, given: str) -> str:
    # Strip AV tags if possible
    try:
        correct = aqt.mw.col.media.strip_av_tags(correct)
    except:
        pass

    # Strip HTML tags
    correct = html_to_text_line(correct)

    return compare_answer_no_html(correct, given)

# Up to Anki 2.1.54
Reviewer.correct = correct

# Anki 2.1.56+ (correction was moved to Rust backend)
Collection.compare_answer = compare_answer
