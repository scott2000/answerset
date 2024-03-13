import math
from dataclasses import dataclass
from typing import Optional, Union

from .config import Config

digits = '0123456789'
factor_separator = '?'

@dataclass(frozen=True)
class NumericRange:
    start_index: int
    digit_end_index: int
    end_index: int
    value: Union[int, float]
    factor: Optional[float]

    def accepts(self, other: 'NumericRange', config: Config) -> bool:
        if other.value == self.value:
            return True

        # Find factor from either config or override
        factor = self.factor if self.factor is not None else config.numeric_comparison_factor

        # If factor is 1.0, only accept exact equality
        if factor == 1.0:
            return False

        try:
            big = float(max(self.value, other.value))
            small = float(min(self.value, other.value))

            if factor > 1.0:
                difference_factor = big / small
                return math.isfinite(difference_factor) and difference_factor <= factor
            else:
                difference_factor = small / big
                return math.isfinite(difference_factor) and factor <= difference_factor

        except ZeroDivisionError:
            return False

    def range(self) -> tuple[int, int]:
        return self.start_index, self.digit_end_index

    def length(self) -> int:
        return self.digit_end_index - self.start_index

def skip_digits(answer: list[str], index: int) -> int:
    """Skip over a series of digits, assuming the first digit is valid."""

    index += 1

    while index < len(answer) and answer[index] in digits:
        index += 1

    return index

def skip_float(answer: list[str], index: int) -> int:
    """Skip over a float with optional decimals, assuming the first digit is valid."""

    index = skip_digits(answer, index)

    if index + 1 < len(answer) and answer[index] == '.' and answer[index + 1] in digits:
        index = skip_digits(answer, index + 1)

    return index

def find_numeric_ranges(answer: list[str], allow_factor: bool) -> list[NumericRange]:
    """Find all numeric ranges present in an answer for matching."""

    try:
        result: list[NumericRange] = []

        index = 0
        while index < len(answer):
            # Find next digit
            if answer[index] not in digits:
                index += 1
                continue

            # Skip over valid float
            start_index = index
            index = skip_float(answer, start_index)
            digit_end_index = index

            # Parse float
            value_str = ''.join(answer[start_index:digit_end_index])
            value = float(value_str) if '.' in value_str else int(value_str)

            factor: Optional[float] = None

            # Check for factor annotation
            if allow_factor and index + 1 < len(answer) and answer[index] == factor_separator and answer[index + 1] in digits:
                factor_start_index = index + 1
                index = skip_float(answer, factor_start_index)
                factor = float(''.join(answer[factor_start_index:index]))

            result.append(NumericRange(start_index, digit_end_index, index, value, factor))

        return result

    except ValueError:
        return []

def find_numeric_ranges_by_end_index(answer: list[str], allow_factor: bool) -> dict[int, NumericRange]:
    return {range.digit_end_index: range for range in find_numeric_ranges(answer, allow_factor)}
