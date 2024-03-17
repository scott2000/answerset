import html
import re
import unicodedata as ucd
from typing import Optional

from . import util

from .arrange import Choice, arrange
from .config import Config
from .diff import ErrorKind, diff
from .group import group_combining

code_close_open_re = re.compile(r"</code><code>")

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

def split_options(config: Config, string: str, sep: Optional[str], bracket_ranges: list[tuple[int, int]]) -> list[Choice]:
    """
    Split a string on a separator, trim whitespace, and remove a comment
    delimited by square brackets.
    """

    stripped = []
    for part in util.split_except_for_ranges(string, sep, bracket_ranges):
        s = part.strip()
        if s:
            stripped.append(split_comment(s, '[', ']', config.answer_choice_comments))

    return stripped

def pick_separator(config: Config, correct: str, correct_bracket_ranges: list[tuple[int, int]]) -> Optional[str]:
    """Pick a separator based on the separators config option."""

    for sep in config.separators:
        if util.has_separator(correct, sep, correct_bracket_ranges):
            return sep

    return None

def format_separator(sep: Optional[str]) -> str:
    if sep == ';' or sep == ',':
        return f'{sep} '
    elif sep and sep != ' ':
        return f' {sep} '
    else:
        return ' '

def withClass(c: str, s: str) -> str:
    return f"<span class={c}>{html.escape(s)}</span>" if s else ''

def good(s: str) -> str:
    return withClass('typeGood', s)

def minor_error(s: str) -> str:
    return withClass('typePass', s)

def bad(s: str) -> str:
    return withClass('typeBad', s)

def missed(s: str) -> str:
    return withClass('typeMissed', s)

def not_code(s: str) -> str:
    return f"</code>{s}<code>" if s else ''

# TODO: consider refactoring this into a DiffRenderer class
def render_diffs(config: Config, given_choice: Choice, correct_choice: Choice, given_elems: list[str], correct_elems: list[str]) -> tuple[bool, int]:
    """Create the diff comparison strings for each part."""

    # Separate comments from parts
    given_str, given_comment = given_choice
    correct_str, correct_comment = correct_choice

    # Only diff comments if they were given
    if given_comment:
        given_str += given_comment
        correct_str += correct_comment

    # Group combining characters to give cleaner diffs
    given = group_combining(given_str)
    correct = group_combining(correct_str)

    has_error = False
    correct_count = 0
    given_elem = ''
    correct_elem = ''

    given_index = 0
    correct_index = 0

    printed_given_error_last = False

    # Iterate through errors to render the diff
    for error in diff(config, correct, given):
        given_start, given_end = error.given_range
        correct_start, correct_end = error.correct_range

        if given_start != given_index:
            printed_given_error_last = False

        given_elem += good(''.join(given[given_index:given_start]))
        correct_elem += good(''.join(correct[correct_index:correct_start]))
        correct_count += correct_start - correct_index

        error_text = ''.join(given[given_start:given_end])
        missing_text = ''.join(correct[correct_start:correct_end])

        if error.kind == ErrorKind.REGULAR:
            if error_text:
                has_error = True
                printed_given_error_last = True
                given_elem += bad(error_text)
            elif error.report and not printed_given_error_last:
                has_error = True
                printed_given_error_last = True
                given_elem += bad('-')

            correct_elem += missed(missing_text)
        elif error.kind == ErrorKind.MINOR:
            has_error = True
            printed_given_error_last = False
            given_elem += minor_error(error_text)
            correct_elem += minor_error(missing_text)

        given_index = given_end
        correct_index = correct_end

    given_elem += good(''.join(given[given_index:]))
    correct_elem += good(''.join(correct[correct_index:]))
    correct_count += len(correct) - correct_index

    # If a comment wasn't diffed, add it back
    if correct_comment and not given_comment:
        correct_elem += not_code(html.escape(correct_comment))

    # Append the diffs to the arrays
    if given_str:
        given_elems.append(given_elem)
    correct_elems.append(correct_elem)

    # Return whether there was any error or not
    return has_error, correct_count

def compare_answer_no_html(config: Config, correct: str, given: str) -> str:
    """Display the corrections for a type-in answer."""

    # Replace consecutive spaces with a single space
    given = config.space_re.sub(' ', given)
    correct = config.space_re.sub(' ', correct)

    # Normalize using NFC to make comparison consistent
    given = ucd.normalize('NFC', given)
    correct = ucd.normalize('NFC', correct)

    # Remove comments in parentheses
    correct, correct_comment = split_comment(correct, '(', ')', config.answer_comments)

    # Only separate comment for given if present for correct
    if correct_comment:
        given, given_comment = split_comment(given, '(', ')', config.answer_comments)
    else:
        given_comment = ''

    # Find bracket ranges in both answers (if config option enabled)
    if config.ignore_separators_in_brackets:
        given_bracket_ranges = util.find_bracket_ranges(given)
        correct_bracket_ranges = util.find_bracket_ranges(correct)
    else:
        given_bracket_ranges = []
        correct_bracket_ranges = []

    sep = pick_separator(config, correct, correct_bracket_ranges)

    # Split on the separator
    given_split = split_options(config, given, sep, given_bracket_ranges)
    correct_split = split_options(config, correct, sep, correct_bracket_ranges)

    # Arrange the parts so that similar ones line up and render the diffs
    has_error = False
    correct_count = 0
    given_elems: list[str] = []
    correct_elems: list[str] = []
    for given_choice, correct_choice in arrange(config, given_split, correct_split):
        if given_choice and correct_choice:
            diff_error, diff_correct = render_diffs(config, given_choice, correct_choice, given_elems, correct_elems)
            has_error |= diff_error
            correct_count += diff_correct
        elif correct_choice:
            # Ignore result since this isn't a real diff
            render_diffs(config, ('', ''), correct_choice, given_elems, correct_elems)
        elif given_choice:
            has_error = True
            given_elems.append(bad(''.join(given_choice)))

    # If there was an error and some of the correct answer choices were missing,
    # the user may have just forgotten to type a separator.
    if has_error and sep and len(given_elems) < len(correct_elems):
        alt_given = given.strip()
        alt_correct = correct.strip()

        original_length = sum(len(answer) + len(comment) for answer, comment in correct_split)
        length_diff = max(0, len(alt_correct) - original_length)

        alt_given_elems: list[str] = []
        alt_correct_elems: list[str] = []
        alt_has_error, alt_correct_count = render_diffs(config, (alt_given, ''), (alt_correct, ''), alt_given_elems, alt_correct_elems)

        # If the diff without splitting is more correct, then don't split
        if alt_correct_count - length_diff > correct_count:
            sep = None
            has_error = alt_has_error
            correct_count = alt_correct_count
            given_elems = alt_given_elems
            correct_elems = alt_correct_elems

    # Diff comments if they were given
    if given_comment:
        given = given_comment.strip()
        correct = correct_comment.strip()
        has_error |= render_diffs(config, (given, ''), (correct, ''), given_elems, correct_elems)[0]

    sep = not_code(html.escape(format_separator(sep)))
    res = '<div id=typeans><code>'

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

    # Merge adjacent code tags
    res = code_close_open_re.sub('', res)

    return res
