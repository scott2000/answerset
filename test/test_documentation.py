from answerset.compare import compare_answer_no_html
from answerset.config import Config

test_config = Config()


def test_doc_first_example() -> None:
    correct = "depart, go, leave"
    given = "leave, go"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>leave</span></code>, <code><span class=typeGood>go</span></code>, <code><span class=typeMissed>depart</span></code></div>"


def test_doc_indic_scripts() -> None:
    correct = "திரும்பு"
    given = "திரமபு"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>தி</span><span class=typeBad>ரம</span><span class=typeGood>பு</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>தி</span><span class=typeMissed>ரும்</span><span class=typeGood>பு</span></code></div>"


def test_doc_semicolon() -> None:
    correct = "a, b, c; d, e, f"
    given = "a, b, c"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>a, b, c</span></code>; <code><span class=typeMissed>d, e, f</span></code></div>"


def test_doc_lenient_validation_missing_hyphen_period() -> None:
    correct = "We co-operated."
    given = "We cooperated"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>We co</span><span class=typeMissed>-</span><span class=typeGood>operated</span><span class=typeMissed>.</span></code></div>"


def test_doc_lenient_validation_missing_paren_text() -> None:
    correct = "start(ing)"
    given = "start"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>start</span><span class=typeMissed>(ing)</span></code></div>"


def test_doc_lenient_validation_missing_parens() -> None:
    correct = "start(ing)"
    given = "starting"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>start</span><span class=typeMissed>(</span><span class=typeGood>ing</span><span class=typeMissed>)</span></code></div>"


def test_doc_lenient_validation_missing_alternative() -> None:
    correct = "set in one's/my ways"
    given = "set in my ways"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>set in </span><span class=typeMissed>one&#x27;s/</span><span class=typeGood>my ways</span></code></div>"


def test_doc_lenient_validation_missing_alternative_with_spaces() -> None:
    correct = "we've got [a lot of/plenty of] time"
    given = "we've got a lot of time"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>we&#x27;ve got </span><span class=typeMissed>[</span><span class=typeGood>a lot of</span><span class=typeMissed>/plenty of]</span><span class=typeGood> time</span></code></div>"


def test_doc_lenient_validation_missing_alternative_bracket() -> None:
    correct = "we've got [a lot of/plenty of] time"
    given = "we've got time"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>we&#x27;ve got </span><span class=typeMissed>[a lot of/plenty of] </span><span class=typeGood>time</span></code></div>"


def test_doc_answer_choice_comments() -> None:
    correct = "dog, cat, mouse [animal]"
    given = "mouse, cow"
    config = Config({
        "Enable Answer Choice Comments [...]": True,
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>mouse</span></code>, <code><span class=typeGood>c</span><span class=typeBad>ow</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>mouse</span></code> [animal]<code></code>, <code><span class=typeGood>c</span><span class=typeMissed>at</span></code>, <code><span class=typeMissed>dog</span></code></div>"


def test_doc_answer_comments() -> None:
    correct = "dog, cat, mouse (animals)"
    given = "mouse, cow"
    config = Config({
        "Enable Answer Comments (...)": True,
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>mouse</span></code>, <code><span class=typeGood>c</span><span class=typeBad>ow</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>mouse</span></code>, <code><span class=typeGood>c</span><span class=typeMissed>at</span></code>, <code><span class=typeMissed>dog</span></code> (animals)<code></code></div>"


def test_doc_numeric_missing_decimals() -> None:
    correct = "$1.00"
    given = "$1"
    config = Config({
        "Numeric Comparison Factor": 1.0,
    })
    result = compare_answer_no_html(config, correct, given)
    assert "typearrow" not in result


def test_doc_numeric_comparison() -> None:
    correct = "215.0 m/s east"
    given = "200 m/s east"
    config = Config({
        "Numeric Comparison Factor": 1.25,
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == "<div id=typeans><code><span class=typePass>200</span><span class=typeGood> m/s east</span><br><span id=typearrow>&darr;</span><br><span class=typePass>215.0</span><span class=typeGood> m/s east</span></code></div>"


def test_doc_numeric_comparison_disabled() -> None:
    correct = "215.0 m/s east"
    given = "200 m/s east"
    config = Config({
        "Numeric Comparison Factor": 0.0,
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == "<div id=typeans><code><span class=typeGood>2</span><span class=typeBad>0</span><span class=typeGood>0 m/s east</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>2</span><span class=typeMissed>15.</span><span class=typeGood>0 m/s east</span></code></div>"


def test_doc_numeric_factor_override() -> None:
    correct = "3.14159?0.999"
    given = "3.14"
    config = Config({
        "Numeric Comparison Factor": 1.0,
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == "<div id=typeans><code><span class=typePass>3.14</span><br><span id=typearrow>&darr;</span><br><span class=typePass>3.14159</span></code></div>"
