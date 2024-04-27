import collections
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from . import util

from .config import Config, casefold_if_ignore_case
from .group import group_combining, has_multiple_chars
from .numeric import find_numeric_ranges_by_end_index

# Exact matches need the highest possible matched count
max_matched = 0x7fffffff

def is_alternative_stop(config: Config, ch: str) -> bool:
    """Check if a character should stop an alternative outside of brackets."""
    return not ch.isalnum() and ch not in config.allow_alternative_continue

def find_alternative_jumps(config: Config, correct: list[str], correct_bracket_ranges: list[tuple[int, int]]) -> dict[int, list[int]]:
    """
    Find out which parts of the correct answer are allowed to be missing since
    they are part of an alternative. Returns a dictionary mapping from end
    index to a list of start indices.
    """

    if '/' not in correct:
        return {}

    bracket_jumps: dict[int, int] = {(end - 1): start for start, end in correct_bracket_ranges}
    bracket_starts: set[int] = {start for start, _ in correct_bracket_ranges}

    jumps: dict[int, list[int]] = {}

    # All of the logic for this function will be run twice, once for stopping
    # alternatives on spaces while inside of brackets, and once for allowing
    # spaces inside of alternatives while inside of brackets.
    def add_jumps(allow_spaces_in_brackets: bool) -> bool:
        # Version of is_alternative_stop() adjusted for allowing spaces in brackets
        def stop(i: int) -> bool:
            ch = correct[i]

            if not is_alternative_stop(config, ch):
                return False

            return not allow_spaces_in_brackets \
                or ch == '/' \
                or ch in config.bracket_chars \
                or not util.index_in_any_range(i, correct_bracket_ranges)

        # In the first iteration, we want to know whether any slashes were
        # inside of brackets so that we know to run the second iteration
        had_slash_in_brackets = False

        # This list tracks the index of the first alpha character in an alternative
        first_alpha: list[Optional[int]] = [None for _ in range(len(correct))]

        # This list tracks the index of the slash immediately before an alternative
        first_slash = first_alpha[:]

        for i, ch in enumerate(correct):
            if ch == '/' and i > 0 and first_alpha[i - 1] is not None:
                first_slash[i] = i
                had_slash_in_brackets = had_slash_in_brackets or util.index_in_any_range(i, correct_bracket_ranges)
                continue

            if i in bracket_jumps:
                jump = bracket_jumps[i]
                if jump > 0:
                    first_alpha[i] = first_alpha[jump - 1]
                    first_slash[i] = first_slash[jump - 1]

                    first_alpha[jump - 1] = None
                    first_slash[jump - 1] = None

                if first_alpha[i] is None:
                    first_alpha[i] = jump

            if stop(i):
                continue

            prev_alpha = first_alpha[i - 1] if i > 0 else None
            prev_slash = first_slash[i - 1] if i > 0 else None

            if prev_alpha is None:
                first_alpha[i] = i
            else:
                first_alpha[i - 1] = None
                first_alpha[i] = prev_alpha

            if prev_slash is not None:
                first_slash[i - 1] = None
                first_slash[i] = prev_slash

        # Using the info in first_alpha and first_slash, find the valid jumps
        for i in range(len(correct) + 1):
            curr_ch = correct[i] if i < len(correct) else None

            prev_slash = first_slash[i - 1] if i > 0 else None
            if prev_slash is not None and prev_slash != i - 1 and (curr_ch is None or stop(i)):
                current = jumps.setdefault(i, [])
                if prev_slash not in current:
                    current.append(prev_slash)

            if curr_ch == '/' and i < len(correct) - 1 and ((i + 1) in bracket_starts or not stop(i + 1)):
                prev_alpha = first_alpha[i - 1] if i > 0 else None
                if prev_alpha is not None:
                    current = jumps.setdefault(i + 1, [])
                    if prev_alpha not in current:
                        current.append(prev_alpha)

        return had_slash_in_brackets

    if add_jumps(False) and correct_bracket_ranges:
        add_jumps(True)

    return jumps

def ends_with(answer: list[str], end: int, to_check: list[str]) -> bool:
    """Check if an answer prefix ends with a certain substring."""

    start = end - len(to_check)
    if start < 0:
        return False

    for i in range(0, len(to_check)):
        if answer[start + i] != to_check[i]:
            return False

    return True

class ErrorKind(Enum):
    REGULAR = 0
    MINOR = 1
    SKIP = 2

@dataclass(frozen=True)
class ErrorRange:
    __slots__ = 'correct_range', 'given_range', 'report', 'kind'

    correct_range: tuple[int, int]
    given_range: tuple[int, int]
    report: bool
    kind: ErrorKind

@dataclass(frozen=True)
class Diff:
    __slots__ = 'matched_count', 'reported_error_count', 'error_ranges', 'current_error_range'

    matched_count: int
    reported_error_count: int
    error_ranges: list[ErrorRange]
    current_error_range: Optional[ErrorRange]

    def add_matched(self, count: int = 1) -> 'Diff':
        return self.replace_error(None, count)

    def add_error(self, error: ErrorRange, matches: int = 0) -> 'Diff':
        if self.current_error_range:
            (ca, cb) = self.current_error_range.correct_range
            (cc, cd) = error.correct_range

            (ga, gb) = self.current_error_range.given_range
            (gc, gd) = error.given_range

            if cb == cc and gb == gc and error.kind == self.current_error_range.kind:
                return Diff(
                    self.matched_count + matches,
                    self.reported_error_count,
                    self.error_ranges,
                    ErrorRange((ca, cd), (ga, gd), self.current_error_range.report or error.report, error.kind))

        return self.replace_error(error, matches)

    def replace_error(self, new_error: Optional[ErrorRange], matches: int = 0) -> 'Diff':
        reported_error_count = self.reported_error_count
        error_ranges = self.error_ranges

        if self.current_error_range:
            if self.current_error_range.report:
                reported_error_count += 1

            error_ranges = self.error_ranges + [self.current_error_range]

        return Diff(self.matched_count + matches, reported_error_count, error_ranges, new_error)

    def reported_error_count_including_current(self) -> int:
        if self.current_error_range is None or not self.current_error_range.report:
            return self.reported_error_count
        else:
            return self.reported_error_count + 1

    def error_range_count_including_current(self) -> int:
        if self.current_error_range is None:
            return len(self.error_ranges)
        else:
            return len(self.error_ranges) + 1

    def prefix_match(self) -> int:
        error_range = self.error_ranges[0] if self.error_ranges else self.current_error_range
        if not error_range:
            return max_matched

        return min(error_range.correct_range[0], error_range.given_range[0])

    def pick_best(self, other: Optional['Diff']) -> 'Diff':
        if other is None or self.is_better_than(other):
            return self
        else:
            return other

    def is_better_than(self, other: 'Diff') -> bool:
        # Higher matched count is better
        if self.matched_count != other.matched_count:
            return self.matched_count > other.matched_count

        # Lower reported error count is better
        self_errors = self.reported_error_count_including_current()
        other_errors = other.reported_error_count_including_current()
        if self_errors != other_errors:
            return self_errors < other_errors

        # Lower total error range count is better
        self_errors = self.error_range_count_including_current()
        other_errors = other.error_range_count_including_current()
        if self_errors != other_errors:
            return self_errors < other_errors

        # It's better to already have an error range since it could expand
        if (self.current_error_range is None) != (other.current_error_range is None):
            return self.current_error_range is not None

        # It's better to already have a reporting error range since it could expand
        if self.current_error_range and other.current_error_range and self.current_error_range.report != other.current_error_range.report:
            return self.current_error_range.report

        # Longer prefix match is better
        self_prefix_match = self.prefix_match()
        other_prefix_match = other.prefix_match()
        return self_prefix_match > other_prefix_match

# Diff representing an exact match with no error ranges
exact_match_diff = Diff(max_matched, 0, [], None)

def casefold_and_record_split_strings(ch: str, split_strings: dict[str, list[str]]) -> str:
    new_ch = ch.casefold()

    if new_ch not in split_strings and has_multiple_chars(new_ch):
        split_strings[new_ch] = group_combining(new_ch)

    return new_ch

def diff(config: Config, given: list[str], correct: list[str]) -> Diff:
    """
    Find the differences between the correct answer and the given answer and
    return a list of errors. If lenient validation is enabled, don't mark
    missing bracketed text, alternative segments, or junk characters as
    reported errors. Checks for equivalent strings while finding difference.
    """

    # There may be more equivalent strings added after case folding
    all_equivalent_strings = config.equivalent_strings

    # If ignoring case, apply Unicode case folding to both
    if config.ignore_case:
        split_strings: dict[str, list[str]] = {}

        correct = list(map(lambda ch: casefold_and_record_split_strings(ch, split_strings), correct))
        given = list(map(lambda ch: casefold_and_record_split_strings(ch, split_strings), given))

        # Record any new equivalences caused by case folding in correct or given
        # Example: ['ß'] expands to ['ss'], but ['s', 's'] is equivalent
        if split_strings:
            all_equivalent_strings = all_equivalent_strings[:]
            for new_ch in split_strings:
                all_equivalent_strings.append([[new_ch], split_strings[new_ch]])

    correct_numeric_ranges = {}
    given_numeric_ranges = {}

    # If numeric comparison is enabled, find all numeric ranges in both answers
    if config.numeric_comparison_factor > 0.0:
        correct_numeric_ranges = find_numeric_ranges_by_end_index(correct, True)

        if correct_numeric_ranges:
            given_numeric_ranges = find_numeric_ranges_by_end_index(given, False)

    # Find ranges to skip over for factor overrides
    factor_skips = {range.end_index: range.digit_end_index for range in correct_numeric_ranges.values() if range.factor is not None}

    if not given and not factor_skips:
        return Diff(0, 0, [ErrorRange((0, len(correct)), (0, 0), False, ErrorKind.REGULAR)], None)

    # If lenient validation is enabled, pre-compute the list of jumps which
    # are allowed to skip over parts which are allowed to be missing
    if config.lenient_validation:
        correct_bracket_ranges = util.find_bracket_ranges(correct, lenient=True, nested=True)

        jumps: dict[int, list[int]] = find_alternative_jumps(config, correct, correct_bracket_ranges)
        for start, end in correct_bracket_ranges:
            jumps.setdefault(end, []).append(start)

        # Make sure the jumps are sorted for consistency
        for end in jumps:
            jumps[end].sort()
    else:
        jumps = {}

    empty_diff = Diff(0, 0, [], None)
    empty_diff_by_correct = [empty_diff for _ in range(len(correct) + 1)]

    # Tracks the best diff for each substring of "correct" in the current iteration
    best_diff_by_correct = empty_diff_by_correct[:]

    # Calculate the number of previous iterations to keep (min: 1)
    given_numeric_lookbehind = max((range.end_index - range.start_index for range in given_numeric_ranges.values()), default=0)
    equivalent_string_lookbehind = max((len(x) for xs in all_equivalent_strings for x in xs), default=0)
    diff_lookbehind = max(1, given_numeric_lookbehind, equivalent_string_lookbehind)

    # Tracks the best diff for each substring of "correct" in previous iterations
    best_diff_by_correct_and_prev_given_queue = collections.deque([empty_diff_by_correct[:]], diff_lookbehind)

    # Iterate over all possible substrings of "given"
    for given_end in range(len(given) + 1):
        given_char = given[given_end - 1] if given_end > 0 else None

        # Iterate over all possible substrings of "correct"
        for correct_end in range(len(correct) + 1):
            correct_char = correct[correct_end - 1] if correct_end > 0 else None

            # Comparison of empty given and empty correct gives empty diff
            if not given_char and not correct_char:
                continue

            best_diff: Optional[Diff] = None

            if correct_char:
                report_missing = not config.lenient_validation or not util.is_junk(config, correct_char)

                # Handle "correct" character missing
                best_diff = best_diff_by_correct[correct_end - 1] \
                    .add_error(ErrorRange((correct_end - 1, correct_end), (given_end, given_end), report_missing, ErrorKind.REGULAR)) \
                    .pick_best(best_diff)

                # Can also skip over missing factor overrides
                if correct_end in factor_skips:
                    skip = factor_skips[correct_end]

                    best_diff = best_diff_by_correct[skip] \
                        .add_error(ErrorRange((skip, correct_end), (given_end, given_end), False, ErrorKind.SKIP), correct_end - skip) \
                        .pick_best(best_diff)

                # Can also jump backwards for missing brackets/alternatives
                for jump in jumps.get(correct_end, ()):
                    best_diff = best_diff_by_correct[jump] \
                        .add_error(ErrorRange((jump, correct_end), (given_end, given_end), False, ErrorKind.REGULAR)) \
                        .pick_best(best_diff)

            # Handle "given" character wrong
            if given_char:
                best_diff = best_diff_by_correct_and_prev_given_queue[-1][correct_end] \
                    .add_error(ErrorRange((correct_end, correct_end), (given_end - 1, given_end), True, ErrorKind.REGULAR)) \
                    .pick_best(best_diff)

            # Handle "given" character matching "correct" character
            if given_char == correct_char:
                best_diff = best_diff_by_correct_and_prev_given_queue[-1][correct_end - 1] \
                    .add_matched() \
                    .pick_best(best_diff)

            if correct_char and given_char:
                # Handle matching equivalent strings
                for equivalent_strings in all_equivalent_strings:
                    for a in equivalent_strings:
                        if not ends_with(given, given_end, a):
                            continue

                        for b in equivalent_strings:
                            if a == b or not ends_with(correct, correct_end, b):
                                continue

                            best_diff = best_diff_by_correct_and_prev_given_queue[-len(a)][correct_end - len(b)] \
                                .add_matched(min(len(a), len(b))) \
                                .pick_best(best_diff)

                # Handle numeric comparisons
                if given_end in given_numeric_ranges and correct_end in correct_numeric_ranges:
                    given_numeric_range = given_numeric_ranges[given_end]
                    correct_numeric_range = correct_numeric_ranges[correct_end]

                    given_numeric_len = given_numeric_range.length()
                    correct_numeric_len = correct_numeric_range.length()

                    numeric_diff = best_diff_by_correct_and_prev_given_queue[-given_numeric_len][correct_numeric_range.start_index]

                    # Mark every digit as matching and add one to ensure numeric comparison is prioritized
                    numeric_matched = min(given_numeric_len, correct_numeric_len) + 1

                    if correct_numeric_range.value == given_numeric_range.value:
                        # If correct, just add matched without an error
                        numeric_diff = numeric_diff.add_matched(numeric_matched)
                    else:
                        # Otherwise, check for minor error within comparison factor
                        minor = correct_numeric_range.accepts(given_numeric_range, config)
                        kind = ErrorKind.MINOR if minor else ErrorKind.REGULAR

                        numeric_error = ErrorRange(correct_numeric_range.range(), given_numeric_range.range(), not minor, kind)
                        numeric_diff = numeric_diff.add_error(numeric_error, numeric_matched)

                    best_diff = numeric_diff.pick_best(best_diff)

            if best_diff:
                best_diff_by_correct[correct_end] = best_diff

        # Push the current list into a queue for later iterations
        best_diff_by_correct_and_prev_given_queue.append(best_diff_by_correct)
        best_diff_by_correct = empty_diff_by_correct[:]

    # Return the error ranges from the best diff for the whole strings
    return best_diff_by_correct_and_prev_given_queue[-1][-1] \
        .replace_error(None)

# Answer choice and comment tuple
Choice = tuple[str, str]

# Placeholder for missing choice when matching answers
empty_choice: Choice = ('', '')

class ChoicePair:
    __slots__ = 'config', 'given', 'correct', 'correct_comment', 'cached_diff'

    def __init__(self, config: Config, given_choice: Choice, correct_choice: Choice) -> None:
        self.config = config

        # Separate comments from parts
        given_str, given_comment = given_choice
        correct_str, correct_comment = correct_choice

        # If a comment was given, add both comments to the strings
        if given_comment:
            given_str += given_comment
            correct_str += correct_comment
            self.correct_comment = ''
        else:
            self.correct_comment = correct_comment

        # Group combining characters to give cleaner diffs
        self.given = group_combining(given_str)
        self.correct = group_combining(correct_str)

        given_casefolded = casefold_if_ignore_case(given_str, self.config.ignore_case)
        correct_casefolded = casefold_if_ignore_case(correct_str, self.config.ignore_case)

        # If exact match, set cached diff immediately
        self.cached_diff: Optional[Diff] = exact_match_diff if given_casefolded == correct_casefolded else None

    def diff(self) -> Diff:
        if self.cached_diff:
            return self.cached_diff

        self.cached_diff = diff(self.config, self.given, self.correct)
        return self.cached_diff

    def is_better_than(self, other: Optional['ChoicePair']) -> bool:
        return other is None or self.diff().is_better_than(other.diff())

    def is_exact_match(self) -> bool:
        return self.cached_diff is not None and self.cached_diff.matched_count == max_matched

    def error_ranges(self) -> list[ErrorRange]:
        return self.diff().error_ranges
