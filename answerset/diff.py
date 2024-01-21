from dataclasses import dataclass
from typing import Optional

import answerset.config as config
import answerset.util as util

def is_alternative_stop(ch: str) -> bool:
    """Check if a character should stop an alternative outside of brackets."""
    return not ch.isalnum() and ch not in config.allow_alternative_continue

def find_alternative_jumps(correct: list[str], correct_bracket_ranges: list[tuple[int, int]]) -> dict[int, list[int]]:
    """
    Find out which parts of the correct answer are allowed to be missing since
    they are part of an alternative. Returns a dictionary mapping from end
    index to a list of start indices.
    """

    if '/' not in correct:
        return {}

    jumps: list[list[int]] = [[] for _ in range(len(correct))]

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

            if not is_alternative_stop(ch):
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
            ch = correct[i] if i < len(correct) else None

            prev_slash = first_slash[i - 1] if i > 0 else None
            if prev_slash is not None and prev_slash != i - 1 and (ch is None or stop(i)):
                current = jumps.setdefault(i, [])
                if prev_slash not in current:
                    current.append(prev_slash)

            if ch == '/' and i < len(correct) - 1 and ((i + 1) in bracket_starts or not stop(i + 1)):
                prev_alpha = first_alpha[i - 1] if i > 0 else None
                if prev_alpha is not None:
                    current = jumps.setdefault(i + 1, [])
                    if prev_alpha not in current:
                        current.append(prev_alpha)

        return had_slash_in_brackets

    if add_jumps(False) and correct_bracket_ranges:
        add_jumps(True)

    return jumps

@dataclass(frozen=True)
class ErrorRange:
    __slots__ = 'correct_range', 'given_range', 'report'

    correct_range: tuple[int, int]
    given_range: tuple[int, int]
    report: bool

@dataclass(frozen=True)
class Diff:
    __slots__ = 'matched_count', 'reported_error_count', 'error_ranges', 'current_error_range'

    matched_count: int
    reported_error_count: int
    error_ranges: list[ErrorRange]
    current_error_range: Optional[ErrorRange]

    def add_matched(self) -> 'Diff':
        return self.replace_error(None, 1)

    def add_error(self, error: ErrorRange) -> 'Diff':
        if self.current_error_range:
            (ca, cb) = self.current_error_range.correct_range
            (cc, cd) = error.correct_range

            (ga, gb) = self.current_error_range.given_range
            (gc, gd) = error.given_range

            if cb == cc and gb == gc:
                return Diff(self.matched_count, self.reported_error_count, self.error_ranges, ErrorRange((ca, cd), (ga, gd), self.current_error_range.report or error.report))

        return self.replace_error(error)

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
        if self.current_error_range is None:
            return False
        if other.current_error_range is None:
            return True

        # It's better to already have a reporting error range since it could expand
        return self.current_error_range.report and not other.current_error_range.report

def diff(correct: list[str], given: list[str]) -> list[ErrorRange]:
    """
    Find the differences between the correct answer and the given answer and
    return a list of errors. If lenient validation is enabled, don't mark
    missing bracketed text, alternative segments, or junk characters as
    reported errors.
    """

    # If ignoring case, convert both to lowercase for diffing
    if config.ignore_case:
        correct = list(map(lambda ch: ch.lower(), correct))
        given = list(map(lambda ch: ch.lower(), given))

    if correct == given:
        return []

    if not given:
        return [ErrorRange((0, len(correct)), (0, 0), False)]

    # If lenient validation is enabled, pre-compute the list of jumps which
    # are allowed to skip over parts which are allowed to be missing
    if config.lenient_validation:
        correct_bracket_ranges = util.find_bracket_ranges(correct, lenient=True, nested=True)

        jumps: dict[int, list[int]] = find_alternative_jumps(correct, correct_bracket_ranges)
        for start, end in correct_bracket_ranges:
            jumps.setdefault(end, []).append(start)
    else:
        jumps = {}

    empty_diff = Diff(0, 0, [], None)

    # Tracks the best diff for each substring of "correct" in the current iteration
    best_diff_by_correct = [empty_diff for _ in range(len(correct) + 1)]

    # Tracks the best diff for each substring of "correct" in the previous iteration
    best_diff_by_correct_and_prev_given = best_diff_by_correct[:]

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

            # Handle "given" character matching "correct" character
            if given_char == correct_char:
                best_diff = best_diff_by_correct_and_prev_given[correct_end - 1].add_matched()

            if correct_char:
                report_missing = not config.lenient_validation or not util.is_junk(correct_char)

                # Handle "correct" character missing
                best_diff = best_diff_by_correct[correct_end - 1] \
                    .add_error(ErrorRange((correct_end - 1, correct_end), (given_end, given_end), report_missing)) \
                    .pick_best(best_diff)

                # Can also jump backwards for missing brackets/alternatives
                for jump in jumps.get(correct_end, ()):
                    best_diff = best_diff_by_correct[jump] \
                        .add_error(ErrorRange((jump, correct_end), (given_end, given_end), False)) \
                        .pick_best(best_diff)

            # Handle "given" character wrong
            if given_char:
                best_diff = best_diff_by_correct_and_prev_given[correct_end] \
                    .add_error(ErrorRange((correct_end, correct_end), (given_end - 1, given_end), True)) \
                    .pick_best(best_diff)

            best_diff_by_correct[correct_end] = best_diff

        # Swap the lists for the next iteration, overwriting anything from the previous iteration
        best_diff_by_correct, best_diff_by_correct_and_prev_given = best_diff_by_correct_and_prev_given, best_diff_by_correct

    # Return the error ranges from the best diff for the whole strings
    return best_diff_by_correct_and_prev_given[-1] \
        .replace_error(None) \
        .error_ranges
