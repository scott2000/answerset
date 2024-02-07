from collections.abc import Iterable

from .config import Config

def is_junk(config: Config, ch: str) -> bool:
    return len(ch) == 1 and ord(ch) in config.junk_trans

def find_bracket_ranges(input: Iterable[str], lenient: bool = False, nested: bool = False) -> list[tuple[int, int]]:
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

            if nested or not expected_ends:
                found_ranges.append((start_index, i + 1))

    if expected_ends and not lenient:
        return []

    return found_ranges

def index_in_any_range(index: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= index < end for start, end in ranges)

def find_indices(haystack: str, needle: str, ranges: list[tuple[int, int]]) -> Iterable[int]:
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
