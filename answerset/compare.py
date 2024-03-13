import html
import unicodedata as ucd

from . import util

from .arrange import Choice, arrange
from .config import Config
from .diff import diff
from .group import group_combining

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

def split_options(config: Config, string: str, sep: str, bracket_ranges: list[tuple[int, int]]) -> list[tuple[str, str]]:
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

def good(s: str) -> str:
    return f"<span class=typeGood>{html.escape(s)}</span>" if s else ''

def bad(s: str) -> str:
    return f"<span class=typeBad>{html.escape(s)}</span>" if s else ''

def missed(s: str) -> str:
    return f"<span class=typeMissed>{html.escape(s)}</span>" if s else ''

def not_code(s: str) -> str:
    return f"</code>{s}<code>" if s else ''

def render_diffs(config: Config, given_choice: Choice, correct_choice: Choice, given_elems: list[str], correct_elems: list[str]):
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
    given_elem = ''
    correct_elem = ''

    given_index = 0
    correct_index = 0

    # Iterate through errors to render the diff
    for error in diff(config, correct, given):
        given_start, given_end = error.given_range
        correct_start, correct_end = error.correct_range

        given_elem += good(''.join(given[given_index:given_start]))
        correct_elem += good(''.join(correct[correct_index:correct_start]))

        error_text = ''.join(given[given_start:given_end])
        if error_text:
            has_error = True
            given_elem += bad(error_text)
        elif error.report:
            has_error = True
            given_elem += bad('-')

        correct_elem += missed(''.join(correct[correct_start:correct_end]))

        given_index = given_end
        correct_index = correct_end

    given_elem += good(''.join(given[given_index:]))
    correct_elem += good(''.join(correct[correct_index:]))

    # If a comment wasn't diffed, add it back
    if correct_comment and not given_comment:
        correct_elem += not_code(html.escape(correct_comment))

    # Append the diffs to the arrays
    given_elems.append(given_elem)
    correct_elems.append(correct_elem)

    # Return whether there was any error or not
    return has_error

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

    # Pick separator as ';' if one is used, otherwise ','
    if util.has_separator(correct, ';', correct_bracket_ranges):
        sep = ';'
    else:
        sep = ','

    # Split on the separator
    given_split = split_options(config, given, sep, given_bracket_ranges)
    correct_split = split_options(config, correct, sep, correct_bracket_ranges)

    # Arrange the parts so that similar ones line up and render the diffs
    has_error: bool = False
    given_elems: list[str] = []
    correct_elems: list[str] = []
    for given_choice, correct_choice in arrange(config, given_split, correct_split):
        if given_choice and correct_choice:
            has_error |= render_diffs(config, given_choice, correct_choice, given_elems, correct_elems)
        elif correct_choice:
            correct_elems.append(missed(correct_choice[0]) + correct_choice[1])
        elif given_choice:
            has_error = True
            given_elems.append(bad(''.join(given_choice)))

    # Diff comments if they were given
    if given_comment:
        given = given_comment.strip()
        correct = correct_comment.strip()
        has_error |= render_diffs(config, (given, ''), (correct, ''), given_elems, correct_elems)

    sep = not_code(html.escape(sep) + ' ')
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

    return res
