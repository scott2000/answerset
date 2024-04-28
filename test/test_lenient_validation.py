from answerset.compare import compare_answer_no_html
from answerset.config import Config

test_config = Config()


def test_no_missing() -> None:
    correct = "test answer"
    given = "test answer"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test answer</span></code></div>"


def test_missing_space() -> None:
    correct = "test answer"
    given = "testanswer"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test</span><span class=typeMissed> </span><span class=typeGood>answer</span></code></div>"


def test_missing_parentheses() -> None:
    correct = "test (word) answer"
    given = "testanswer"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test</span><span class=typeMissed> (word) </span><span class=typeGood>answer</span></code></div>"


def test_missing_alternative_start() -> None:
    correct = "test abc/def/ghi test"
    given = "test abc test"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test abc</span><span class=typeMissed>/def/ghi</span><span class=typeGood> test</span></code></div>"


def test_missing_alternative_middle() -> None:
    correct = "test abc/def/ghi test"
    given = "test def test"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test </span><span class=typeMissed>abc/</span><span class=typeGood>def</span><span class=typeMissed>/ghi</span><span class=typeGood> test</span></code></div>"


def test_missing_alternative_not_middle() -> None:
    correct = "test abc/def/ghi test"
    given = "test abc/ghi test"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test abc/</span><span class=typeMissed>def/</span><span class=typeGood>ghi test</span></code></div>"


def test_missing_alternative_end() -> None:
    correct = "test abc/def/ghi test"
    given = "test ghi test"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test </span><span class=typeMissed>abc/def/</span><span class=typeGood>ghi test</span></code></div>"


def test_missing_alternative_all() -> None:
    correct = "test abc/def/ghi test"
    given = "test test"
    result = compare_answer_no_html(test_config, correct, given)
    assert "typearrow" in result


def test_missing_alternative_start_with_brackets() -> None:
    correct = "test abc/def/ghi (wx yz). test"
    given = "test abc test"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test abc</span><span class=typeMissed>/def/ghi (wx yz).</span><span class=typeGood> test</span></code></div>"


def test_missing_alternative_middle_with_brackets() -> None:
    correct = "test abc/d(e)f/ghi test"
    given = "test def test"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test </span><span class=typeMissed>abc/</span><span class=typeGood>d</span><span class=typeMissed>(</span><span class=typeGood>e</span><span class=typeMissed>)</span><span class=typeGood>f</span><span class=typeMissed>/ghi</span><span class=typeGood> test</span></code></div>"


def test_missing_alternative_not_middle_with_brackets() -> None:
    correct = "test abc/d[ wx yz ]f/ghi test"
    given = "test abc/ghi test"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test abc/</span><span class=typeMissed>d[ wx yz ]f/</span><span class=typeGood>ghi test</span></code></div>"


def test_missing_alternative_end_with_brackets() -> None:
    correct = "test [wx yz]. abc/def/ghi test"
    given = "test ghi test"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test </span><span class=typeMissed>[wx yz]. abc/def/</span><span class=typeGood>ghi test</span></code></div>"


def test_missing_alternative_in_word_with_brackets() -> None:
    correct = "test word(abc/def/ghi)word test"
    given = "test worddefword test"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test word</span><span class=typeMissed>(abc/</span><span class=typeGood>def</span><span class=typeMissed>/ghi)</span><span class=typeGood>word test</span></code></div>"


def test_missing_alternative_with_spaces_in_brackets() -> None:
    correct = "test [a b c/d e f/g h i] test"
    given = "test d e f test"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>test </span><span class=typeMissed>[a b c/</span><span class=typeGood>d e f</span><span class=typeMissed>/g h i]</span><span class=typeGood> test</span></code></div>"


def test_missing_alternative_with_spaces_not_in_brackets() -> None:
    correct = "test a b c/d e f/g h i test"
    given = "test d e f test"
    result = compare_answer_no_html(test_config, correct, given)
    assert "typearrow" in result


def test_missing_alternative_with_space_before_slash() -> None:
    correct = "test abc /def/ghi test"
    given = "test abc test"
    result = compare_answer_no_html(test_config, correct, given)
    assert "typearrow" in result


def test_several_lenient_validation_together() -> None:
    options = [
        ("ac/cb/cc ", "ac "),
        ("ac/cb/cc ", "ac/cb "),
        ("ac/cb/cc ", "ac/cc "),
        ("ac/cb/cc ", "cb "),
        ("ac/cb/cc ", "cb/cc "),
        ("ac/cb/cc ", "cc "),
        ("[ac/cb/cc] ", "ac "),
        ("[ac/cb/cc] ", "ac/cb "),
        ("[ac/cb/cc] ", "ac/cc "),
        ("[ac/cb/cc] ", "cb "),
        ("[ac/cb/cc] ", "cb/cc "),
        ("[ac/cb/cc] ", "cc "),
        ("[ac/cb/cc] ", ""),
        ("[a c/c b/cc] ", "a c "),
        ("[a c/c b/cc] ", "a c/c b "),
        ("[a c/c b/cc] ", "a c/cc "),
        ("[a c/c b/cc] ", "c b "),
        ("[a c/c b/cc] ", "c b/cc "),
        ("[a c/c b/cc] ", "cc "),
        ("[a c/c b/cc] ", ""),
        ("[ac/c b/cc] ", "ac b "),
        ("[ac/c b/cc] ", "ac cc "),
        ("[ac/c b/cc] ", "c b "),
        ("[ac/c b/cc] ", "c cc "),
    ]

    bTrans = str.maketrans("abc", "def")

    for correctA, givenA in options:
        for correctB, givenB in options:
            correct = f"x {correctA}{correctB.translate(bTrans)}{correctA.translate(bTrans)}y"
            given = f"x {givenA}{givenB.translate(bTrans)}{givenA.translate(bTrans)}y"
            result = compare_answer_no_html(test_config, correct, given)
            assert "typearrow" not in result, f"{given} :: {correct}"
