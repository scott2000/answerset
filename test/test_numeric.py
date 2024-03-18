from answerset.compare import compare_answer_no_html
from answerset.config import Config
from answerset.numeric import NumericRange, find_numeric_ranges

def factor(f: float) -> Config:
    return Config({
        "Numeric Comparison Factor": f,
    })

def test_numeric_range_exact_match_1() -> None:
    correct = NumericRange(0, 0, 0, 12.3456, None)
    given = NumericRange(0, 0, 0, 12.3456, None)
    assert correct.accepts(given, factor(1.0))

def test_numeric_range_exact_match_2() -> None:
    correct = NumericRange(0, 0, 0, 12.3456, 1.0)
    given = NumericRange(0, 0, 0, 12.3456, None)
    assert correct.accepts(given, factor(1.5))

def test_numeric_range_exact_match_3() -> None:
    correct = NumericRange(0, 0, 0, 12.3456, 1.0)
    given = NumericRange(0, 0, 0, 12.3456, None)
    assert correct.accepts(given, factor(1.5))

def test_numeric_range_inexact_match_1() -> None:
    correct = NumericRange(0, 0, 0, 12.3456, None)
    given = NumericRange(0, 0, 0, 12, None)
    assert correct.accepts(given, factor(1.1))

def test_numeric_range_inexact_match_2() -> None:
    correct = NumericRange(0, 0, 0, 12.3456, None)
    given = NumericRange(0, 0, 0, 13, None)
    assert correct.accepts(given, factor(1.1))

def test_numeric_range_inexact_match_3() -> None:
    correct = NumericRange(0, 0, 0, 100, 0.1)
    given = NumericRange(0, 0, 0, 10, None)
    assert correct.accepts(given, factor(1.0))

def test_numeric_range_inexact_match_4() -> None:
    correct = NumericRange(0, 0, 0, 100, None)
    given = NumericRange(0, 0, 0, 1000, None)
    assert correct.accepts(given, factor(0.1))

def test_numeric_range_no_match_1() -> None:
    correct = NumericRange(0, 0, 0, 100, 0.1)
    given = NumericRange(0, 0, 0, 9.999, None)
    assert not correct.accepts(given, factor(1.0))

def test_numeric_range_no_match_2() -> None:
    correct = NumericRange(0, 0, 0, 100, None)
    given = NumericRange(0, 0, 0, 1000.001, None)
    assert not correct.accepts(given, factor(0.1))

def test_numeric_range_no_match_3() -> None:
    correct = NumericRange(0, 0, 0, 1.0, None)
    given = NumericRange(0, 0, 0, 1.00000000001, None)
    assert not correct.accepts(given, factor(1.0))

def test_numeric_range_no_match_4() -> None:
    correct = NumericRange(0, 0, 0, 0.0, None)
    given = NumericRange(0, 0, 0, 0.00000000001, None)
    assert not correct.accepts(given, factor(10000.0))

def test_parse_single_int_1() -> None:
    answer = '0'
    result = [NumericRange(0, 1, 1, 0, None)]
    assert find_numeric_ranges(list(answer), False) == result

def test_parse_single_int_2() -> None:
    answer = '18446744073709551616'
    result = [NumericRange(0, 20, 20, 18446744073709551616, None)]
    assert find_numeric_ranges(list(answer), True) == result

def test_parse_single_int_with_factor_1() -> None:
    answer = '18446744073709551616?2'
    result = [NumericRange(0, 20, 20, 18446744073709551616, None), NumericRange(21, 22, 22, 2, None)]
    assert find_numeric_ranges(list(answer), False) == result

def test_parse_single_int_with_factor_2() -> None:
    answer = '18446744073709551616?2'
    result = [NumericRange(0, 20, 22, 18446744073709551616, 2.0)]
    assert find_numeric_ranges(list(answer), True) == result

def test_parse_single_float_1() -> None:
    answer = '0.0'
    result = [NumericRange(0, 3, 3, 0.0, None)]
    assert find_numeric_ranges(list(answer), False) == result

def test_parse_single_float_2() -> None:
    answer = '12.34'
    result = [NumericRange(0, 5, 5, 12.34, None)]
    assert find_numeric_ranges(list(answer), True) == result

def test_parse_single_float_with_factor_1() -> None:
    answer = '12.34?1.0'
    result = [NumericRange(0, 5, 5, 12.34, None), NumericRange(6, 9, 9, 1.0, None)]
    assert find_numeric_ranges(list(answer), False) == result

def test_parse_single_float_with_factor_2() -> None:
    answer = '12.34?1.0'
    result = [NumericRange(0, 5, 9, 12.34, 1.0)]
    assert find_numeric_ranges(list(answer), True) == result

def test_parse_several_numbers() -> None:
    answer = '.12 3.4.5 6..7. 8.'
    result = [
        NumericRange(1, 3, 3, 12, None),
        NumericRange(4, 7, 7, 3.4, None),
        NumericRange(8, 9, 9, 5, None),
        NumericRange(10, 11, 11, 6, None),
        NumericRange(13, 14, 14, 7, None),
        NumericRange(16, 17, 17, 8, None),
    ]
    assert find_numeric_ranges(list(answer), False) == result

def test_parse_several_numbers_with_factor() -> None:
    answer = '1?? 2?3?4 5?6.7.8?'
    result = [
        NumericRange(0, 1, 1, 1, None),
        NumericRange(4, 5, 7, 2, 3),
        NumericRange(8, 9, 9, 4, None),
        NumericRange(10, 11, 15, 5, 6.7),
        NumericRange(16, 17, 17, 8, None),
    ]
    assert find_numeric_ranges(list(answer), True) == result

def test_number_missing() -> None:
    correct = 'the answer is 12'
    given = 'the answer is twelve'
    result = compare_answer_no_html(factor(1.0), correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>the answer is </span><span class=typeBad>twelve</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>the answer is </span><span class=typeMissed>12</span></code></div>'

def test_number_missing_with_factor() -> None:
    correct = 'the answer is 12?0.9'
    given = 'the answer is twelve'
    result = compare_answer_no_html(factor(1.0), correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>the answer is </span><span class=typeBad>twelve</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>the answer is </span><span class=typeMissed>12</span></code></div>'

def test_number_wrong() -> None:
    correct = 'the answer is 12'
    given = 'the answer is 13'
    result = compare_answer_no_html(factor(1.0), correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>the answer is </span><span class=typeBad>13</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>the answer is </span><span class=typeMissed>12</span></code></div>'

def test_number_wrong_with_factor() -> None:
    correct = 'the answer is 12?0.9'
    given = 'the answer is 42'
    result = compare_answer_no_html(factor(1.0), correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>the answer is </span><span class=typeBad>42</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>the answer is </span><span class=typeMissed>12</span></code></div>'

def test_number_close() -> None:
    correct = 'the answer is 12'
    given = 'the answer is 13'
    result = compare_answer_no_html(factor(1.1), correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>the answer is </span><span class=typePass>13</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>the answer is </span><span class=typePass>12</span></code></div>'

def test_number_close_with_factor() -> None:
    correct = 'the answer is 12?4'
    given = 'the answer is 42'
    result = compare_answer_no_html(factor(1.1), correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>the answer is </span><span class=typePass>42</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>the answer is </span><span class=typePass>12</span></code></div>'

def test_number_exact() -> None:
    correct = 'the answer is 12'
    given = 'the answer is 12.0'
    result = compare_answer_no_html(factor(1.1), correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>the answer is 12</span></code></div>'

def test_number_exact_with_factor() -> None:
    correct = 'the answer is 12?1.0'
    given = 'the answer is 12.0'
    result = compare_answer_no_html(factor(1.1), correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>the answer is 12</span></code></div>'

def test_number_string_comparison() -> None:
    correct = 'the answer is 12'
    given = 'the answer is 12.0'
    result = compare_answer_no_html(factor(0.0), correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>the answer is 12</span><span class=typeBad>.0</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>the answer is 12</span></code></div>'

def test_number_string_comparison_with_factor() -> None:
    correct = 'the answer is 10?1.2'
    given = 'the answer is 12.0'
    result = compare_answer_no_html(factor(0.0), correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>the answer is 1</span><span class=typeBad>2.</span><span class=typeGood>0</span><span class=typeBad>-</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>the answer is 1</span><span class=typeGood>0</span><span class=typeMissed>?1.2</span></code></div>'
