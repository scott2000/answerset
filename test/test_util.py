from answerset.util import find_bracket_ranges

def visualize_range(input: str, bracket_ranges: list[tuple[int, int]]) -> str:
    starts = set(range[0] for range in bracket_ranges)
    ends = set(range[1] - 1 for range in bracket_ranges)

    def show(i: int) -> str:
        if i in starts:
            return '{'
        elif i in ends:
            return '}'
        else:
            return '-'

    return ''.join(show(i) for i in range(len(input)))

def test_find_bracket_ranges_no_brackets() -> None:
    string = 'abc def'
    result = '-------'
    assert visualize_range(string, find_bracket_ranges(string)) == result

def test_find_bracket_ranges_regular() -> None:
    string = 'abc (def) g[h]i'
    result = '----{---}--{-}-'
    assert visualize_range(string, find_bracket_ranges(string)) == result

def test_find_bracket_ranges_nested_1() -> None:
    string = 'abc (d[e]f) ghi'
    result = '----{-----}----'
    assert visualize_range(string, find_bracket_ranges(string)) == result

def test_find_bracket_ranges_nested_2() -> None:
    string = 'abc (d[e]f) ghi'
    result = '----{-{-}-}----'
    assert visualize_range(string, find_bracket_ranges(string, nested=True)) == result

def test_find_bracket_ranges_nested_3() -> None:
    string = 'abc (d(e)f) ghi'
    result = '----{-{-}-}----'
    assert visualize_range(string, find_bracket_ranges(string, nested=True)) == result

def test_find_bracket_ranges_unbalanced_1() -> None:
    string = 'a(bc (d(e)f gh)i'
    result = '----------------'
    assert visualize_range(string, find_bracket_ranges(string, nested=True)) == result

def test_find_bracket_ranges_unbalanced_2() -> None:
    string = 'a(bc d(e)f) gh)i'
    result = '----------------'
    assert visualize_range(string, find_bracket_ranges(string, nested=True)) == result

def test_find_bracket_ranges_unbalanced_3() -> None:
    string = 'a(bc (d[e)f] gh)i'
    result = '-----------------'
    assert visualize_range(string, find_bracket_ranges(string, nested=True)) == result

def test_find_bracket_ranges_lenient_1() -> None:
    string = 'a(bc (d(e)f gh)i'
    result = '-----{-{-}----}-'
    assert visualize_range(string, find_bracket_ranges(string, lenient=True, nested=True)) == result

def test_find_bracket_ranges_lenient_2() -> None:
    string = 'a(bc d(e)f) gh)i'
    result = '-{----{-}-}-----'
    assert visualize_range(string, find_bracket_ranges(string, lenient=True, nested=True)) == result

def test_find_bracket_ranges_lenient_3() -> None:
    string = 'a(bc (d[e)f] gh)i'
    result = '-----------------'
    assert visualize_range(string, find_bracket_ranges(string, lenient=True, nested=True)) == result
