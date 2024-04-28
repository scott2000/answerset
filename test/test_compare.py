from answerset.compare import compare_answer_no_html, split_comment
from answerset.config import Config

test_config = Config()

test_config_with_comments = Config({
    "Enable Answer Choice Comments [...]": True,
    "Enable Answer Comments (...)": True,
})


def test_split_comment_disabled() -> None:
    input = "abc def (ghi)"
    expected = ("abc def (ghi)", "")
    assert split_comment(input, "(", ")", False) == expected


def test_split_comment_regular() -> None:
    input = "abc def (ghi)"
    expected = ("abc def", " (ghi)")
    assert split_comment(input, "(", ")", True) == expected


def test_split_comment_no_comment() -> None:
    input = "abc def"
    expected = ("abc def", "")
    assert split_comment(input, "(", ")", True) == expected


def test_split_comment_too_short() -> None:
    input = "()"
    expected = ("()", "")
    assert split_comment(input, "(", ")", True) == expected


def test_split_comment_nothing_left() -> None:
    input = " (abc)"
    expected = (" (abc)", "")
    assert split_comment(input, "(", ")", True) == expected


def test_split_comment_multiple_parens() -> None:
    input = "(abc) (def)"
    expected = ("(abc) (def)", "")
    assert split_comment(input, "(", ")", True) == expected


def test_split_comment_no_space() -> None:
    input = "abc(def)"
    expected = ("abc(def)", "")
    assert split_comment(input, "(", ")", True) == expected


def test_split_comment_nested_parens() -> None:
    input = "abc (def (ghi))"
    expected = ("abc", " (def (ghi))")
    assert split_comment(input, "(", ")", True) == expected


def test_split_comment_unbalanced_nested_parens_1() -> None:
    input = "abc (def (ghi)"
    expected = ("abc (def (ghi)", "")
    assert split_comment(input, "(", ")", True) == expected


def test_split_comment_unbalanced_nested_parens_2() -> None:
    input = "abc (def ghi))"
    expected = ("abc (def ghi))", "")
    assert split_comment(input, "(", ")", True) == expected


def test_split_comment_unbalanced_nested_parens_3() -> None:
    input = "abc def (ghi))"
    expected = ("abc def (ghi))", "")
    assert split_comment(input, "(", ")", True) == expected


def test_compare_answer_comments_1() -> None:
    correct = "abc, def (ghi)"
    given = "def, abc"
    result = compare_answer_no_html(test_config_with_comments, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>def</span></code>, <code><span class=typeGood>abc</span></code> (ghi)<code></code></div>"


def test_compare_answer_comments_2() -> None:
    correct = "abc, def (ghi)"
    given = "def, abc (ghi)"
    result = compare_answer_no_html(test_config_with_comments, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>def</span></code>, <code><span class=typeGood>abc</span></code>, <code><span class=typeGood>(ghi)</span></code></div>"


def test_compare_answer_comments_3() -> None:
    correct = "abc, def"
    given = "def, abc (ghi)"
    result = compare_answer_no_html(test_config_with_comments, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>def</span></code>, <code><span class=typeGood>abc</span><span class=typeBad> (ghi)</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>def</span></code>, <code><span class=typeGood>abc</span></code></div>"


def test_compare_answer_choice_comments_1() -> None:
    correct = "abc [def], ghi"
    given = "ghi, abc"
    result = compare_answer_no_html(test_config_with_comments, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>ghi</span></code>, <code><span class=typeGood>abc</span></code> [def]<code></code></div>"


def test_compare_answer_choice_comments_2() -> None:
    correct = "abc [def], ghi"
    given = "ghi, abc [def]"
    result = compare_answer_no_html(test_config_with_comments, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>ghi</span></code>, <code><span class=typeGood>abc [def]</span></code></div>"


def test_compare_answer_choice_comments_3() -> None:
    correct = "abc, ghi"
    given = "ghi, abc [def]"
    result = compare_answer_no_html(test_config_with_comments, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>ghi</span></code>, <code><span class=typeGood>abc</span><span class=typeBad> [def]</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>ghi</span></code>, <code><span class=typeGood>abc</span></code></div>"


def test_compare_exact() -> None:
    correct = "abc, def, ghi"
    given = "def, ghi, abc"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>def</span></code>, <code><span class=typeGood>ghi</span></code>, <code><span class=typeGood>abc</span></code></div>"


def test_compare_exact_missing() -> None:
    correct = "abc, def, ghi"
    given = "ghi, abc"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>ghi</span></code>, <code><span class=typeGood>abc</span></code>, <code><span class=typeMissed>def</span></code></div>"


def test_compare_exact_wrong() -> None:
    correct = "abc, def"
    given = "def, ghi, abc"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>def</span></code>, <code><span class=typeBad>ghi</span></code>, <code><span class=typeGood>abc</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>def</span></code>, <code><span class=typeGood>abc</span></code></div>"


def test_compare_duplicate_1() -> None:
    correct = "aaa, aaa"
    given = "aaa"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>aaa</span></code>, <code><span class=typeMissed>aaa</span></code></div>"


def test_compare_duplicate_2() -> None:
    correct = "aaa, aaa"
    given = "aaa, aaa"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>aaa</span></code>, <code><span class=typeGood>aaa</span></code></div>"


def test_compare_duplicate_3() -> None:
    correct = "aaa"
    given = "aaa, aaa"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>aaa</span><span class=typeBad>, aaa</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>aaa</span></code></div>"


def test_compare_duplicate_4() -> None:
    correct = "aaa,"
    given = "aaa, aaa"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>aaa</span></code>, <code><span class=typeBad>aaa</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>aaa</span></code></div>"


def test_compare_duplicate_5() -> None:
    correct = "bbb., aaa-, bbb-, aaa."
    given = "aaa, bbb"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>aaa</span><span class=typeMissed>-</span></code>, <code><span class=typeGood>bbb</span><span class=typeMissed>.</span></code>, <code><span class=typeMissed>bbb-</span></code>, <code><span class=typeMissed>aaa.</span></code></div>"
