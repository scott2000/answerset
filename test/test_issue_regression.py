from answerset.compare import compare_answer_no_html
from answerset.config import Config

test_config = Config()

def test_issue_2_alternative() -> None:
    correct = "be set in one's/my ways"
    given = 'be set in my ways'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>be set in </span><span class=typeMissed>one&#x27;s/</span><span class=typeGood>my ways</span></code></div>'

def test_issue_2_equivalent_strings() -> None:
    correct = "keep one's eye on somebody"
    given = 'keep ones eye on sb'
    config = Config({
        "Enable Lenient Validation": False,
        "Equivalent Strings": [
            ["one's", "ones"],
            ["sb", "somebody"]
        ],
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>keep one&#x27;s eye on somebody</span></code></div>'

def test_issue_2_alternative_in_brackets_first() -> None:
    correct = "There's no need to hurry - we've got [a lot of/plenty of] time."
    given = "There's no need to hurry - we've got a lot of time."
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>There&#x27;s no need to hurry - we&#x27;ve got </span><span class=typeMissed>[</span><span class=typeGood>a lot of</span><span class=typeMissed>/plenty of]</span><span class=typeGood> time.</span></code></div>'

def test_issue_2_alternative_in_brackets_second() -> None:
    correct = "There's no need to hurry - we've got [a lot of/plenty of] time."
    given = "There's no need to hurry - we've got plenty of time."
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>There&#x27;s no need to hurry - we&#x27;ve got </span><span class=typeMissed>[a lot of/</span><span class=typeGood>plenty of</span><span class=typeMissed>]</span><span class=typeGood> time.</span></code></div>'

def test_issue_3_starting() -> None:
    correct = 'start(ing)'
    given = 'start'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>start</span><span class=typeMissed>(ing)</span></code></div>'

def test_issue_4_period_after_bracket() -> None:
    correct = "They're coming at [time]."
    given = "They're coming at"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>They&#x27;re coming at</span><span class=typeMissed> [time].</span></code></div>'

def test_issue_4_periods_at_end() -> None:
    correct = 'en/et favoritt...'
    given = 'en favoritt'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>en</span><span class=typeMissed>/et</span><span class=typeGood> favoritt</span><span class=typeMissed>...</span></code></div>'

def test_issue_4_periods_in_middle() -> None:
    correct = 'ser ... på'
    given = 'ser på'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>ser </span><span class=typeMissed>... </span><span class=typeGood>på</span></code></div>'

def test_issue_5_period_after_alternative() -> None:
    correct = 'Det er X i Yen/Ya.'
    given = 'Det er X i Yen'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>Det er X i Yen</span><span class=typeMissed>/Ya.</span></code></div>'

def test_issue_10_many_missing_chars() -> None:
    correct = 'kler på meg/deg/seg/oss, Xen'
    given = 'kler på meg'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>kler på meg</span><span class=typeMissed>/deg/seg/oss</span></code>, <code><span class=typeMissed>Xen</span></code></div>'

def test_issue_10_separators_in_brackets() -> None:
    correct = 'kler på (meg/deg/seg/oss, Xen, ...)'
    given = 'kler på (meg, Xen, ...)'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>kler på (meg</span><span class=typeMissed>/deg/seg/oss</span><span class=typeGood>, Xen, ...)</span></code></div>'

def test_issue_13_alternative_in_bracket_in_word_first() -> None:
    correct = 'tar en (master/bachelor)grad i X'
    given = 'tar en mastergrad i X'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>tar en </span><span class=typeMissed>(</span><span class=typeGood>master</span><span class=typeMissed>/bachelor)</span><span class=typeGood>grad i X</span></code></div>'

def test_issue_13_alternative_in_bracket_in_word_second() -> None:
    correct = 'tar en (master/bachelor)grad i X'
    given = 'tar en bachelorgrad i X'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>tar en </span><span class=typeMissed>(master/</span><span class=typeGood>bachelor</span><span class=typeMissed>)</span><span class=typeGood>grad i X</span></code></div>'

def test_issue_13_alternative_in_bracket_in_word_both() -> None:
    correct = 'tar en (master/bachelor)grad i X'
    given = 'tar en master/bachelorgrad i X'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>tar en </span><span class=typeMissed>(</span><span class=typeGood>master/bachelor</span><span class=typeMissed>)</span><span class=typeGood>grad i X</span></code></div>'

def test_issue_13_alternative_in_bracket_in_word_neither() -> None:
    correct = 'tar en (master/bachelor)grad i X'
    given = 'tar en grad i X'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>tar en </span><span class=typeMissed>(master/bachelor)</span><span class=typeGood>grad i X</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_1() -> None:
    correct = 'point(ing/s) (at)'
    given = 'pointing at'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>point</span><span class=typeMissed>(</span><span class=typeGood>ing</span><span class=typeMissed>/s)</span><span class=typeGood> </span><span class=typeMissed>(</span><span class=typeGood>at</span><span class=typeMissed>)</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_2() -> None:
    correct = 'point(ing/s) (at)'
    given = 'pointing'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>point</span><span class=typeMissed>(</span><span class=typeGood>ing</span><span class=typeMissed>/s) (at)</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_3() -> None:
    correct = 'point(ing/s) (at)'
    given = 'points at'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>point</span><span class=typeMissed>(ing/</span><span class=typeGood>s</span><span class=typeMissed>)</span><span class=typeGood> </span><span class=typeMissed>(</span><span class=typeGood>at</span><span class=typeMissed>)</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_4() -> None:
    correct = 'point(ing/s) (at)'
    given = 'points'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>point</span><span class=typeMissed>(ing/</span><span class=typeGood>s</span><span class=typeMissed>) (at)</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_5() -> None:
    correct = 'point(ing/s) (at)'
    given = 'point at'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>point</span><span class=typeMissed>(ing/s)</span><span class=typeGood> </span><span class=typeMissed>(</span><span class=typeGood>at</span><span class=typeMissed>)</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_6() -> None:
    correct = 'point(ing/s) (at)'
    given = 'point'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>point</span><span class=typeMissed>(ing/s) (at)</span></code></div>'

def test_issue_18_overlapping_alternatives_1() -> None:
    correct = 'apprenticeship as a/an X'
    given = 'apprenticeship as a X'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>apprenticeship as a</span><span class=typeMissed>/an</span><span class=typeGood> X</span></code></div>'

def test_issue_18_overlapping_alternatives_2() -> None:
    correct = 'apprenticeship as a/an X'
    given = 'apprenticeship as an X'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>apprenticeship as </span><span class=typeMissed>a/</span><span class=typeGood>an X</span></code></div>'

def test_issue_18_overlapping_alternatives_3() -> None:
    correct = 'apprenticeship as an/a X'
    given = 'apprenticeship as an X'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>apprenticeship as an</span><span class=typeMissed>/a</span><span class=typeGood> X</span></code></div>'

def test_issue_18_overlapping_alternatives_4() -> None:
    correct = 'apprenticeship as an/a X'
    given = 'apprenticeship as a X'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>apprenticeship as </span><span class=typeMissed>an/</span><span class=typeGood>a X</span></code></div>'

def test_issue_18_overlapping_alternatives_5() -> None:
    correct = 'start/starting'
    given = 'start'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>start</span><span class=typeMissed>/starting</span></code></div>'

def test_issue_18_overlapping_alternatives_6() -> None:
    correct = 'start/starting'
    given = 'starting'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeMissed>start/</span><span class=typeGood>starting</span></code></div>'

def test_issue_18_overlapping_alternatives_7() -> None:
    correct = 'starting/start'
    given = 'starting'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>starting</span><span class=typeMissed>/start</span></code></div>'

def test_issue_18_overlapping_alternatives_8() -> None:
    correct = 'starting/start'
    given = 'start'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeMissed>starting/</span><span class=typeGood>start</span></code></div>'

def test_issue_18_text_in_alternative_and_after_1() -> None:
    correct = '(am/is/are/being) in good health'
    given = 'am in good health'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeMissed>(</span><span class=typeGood>am</span><span class=typeMissed>/is/are/being)</span><span class=typeGood> in good health</span></code></div>'

def test_issue_18_text_in_alternative_and_after_2() -> None:
    correct = '(am/is/are/being) in good health'
    given = 'is in good health'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeMissed>(am/</span><span class=typeGood>is</span><span class=typeMissed>/are/being)</span><span class=typeGood> in good health</span></code></div>'

def test_issue_18_text_in_alternative_and_after_3() -> None:
    correct = '(am/is/are/being) in good health'
    given = 'are in good health'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeMissed>(am/is/</span><span class=typeGood>are</span><span class=typeMissed>/being)</span><span class=typeGood> in good health</span></code></div>'

def test_issue_18_text_in_alternative_and_after_4() -> None:
    correct = '(am/is/are/being) in good health'
    given = 'being in good health'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeMissed>(am/is/are/</span><span class=typeGood>being</span><span class=typeMissed>)</span><span class=typeGood> in good health</span></code></div>'

def test_issue_18_parentheses_in_alternative_1() -> None:
    correct = 'become(s)/becoming (x)'
    given = 'become'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>become</span><span class=typeMissed>(s)/becoming (x)</span></code></div>'

def test_issue_18_parentheses_in_alternative_2() -> None:
    correct = 'become(s)/becoming (x)'
    given = 'becomes'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>become</span><span class=typeMissed>(</span><span class=typeGood>s</span><span class=typeMissed>)/becoming (x)</span></code></div>'

def test_issue_18_parentheses_in_alternative_3() -> None:
    correct = 'become(s)/becoming (x)'
    given = 'becoming'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeMissed>become(s)/</span><span class=typeGood>becoming</span><span class=typeMissed> (x)</span></code></div>'

def test_issue_18_parentheses_in_alternative_4() -> None:
    correct = 'get(s/ting) (x)'
    given = 'get'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>get</span><span class=typeMissed>(s/ting) (x)</span></code></div>'

def test_issue_18_parentheses_in_alternative_5() -> None:
    correct = 'get(s/ting) (x)'
    given = 'gets'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>get</span><span class=typeMissed>(</span><span class=typeGood>s</span><span class=typeMissed>/ting) (x)</span></code></div>'

def test_issue_18_parentheses_in_alternative_6() -> None:
    correct = 'get(s/ting) (x)'
    given = 'getting'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>get</span><span class=typeMissed>(s/</span><span class=typeGood>ting</span><span class=typeMissed>) (x)</span></code></div>'

def test_issue_23_equivalent_strings() -> None:
    correct = 'I am happy.'
    given = "I'm happy"
    config = Config({
        "Equivalent Strings": [
            ["I'm", "I am"]
        ],
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>I am happy</span><span class=typeMissed>.</span></code></div>'

def test_issue_28_with_separator() -> None:
    correct = 'Da pappa var ung, besøkte han oslo om sommeren.'
    given = 'Da pappa var ung, besøkte han oslo om sommeren'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>Da pappa var ung</span></code>, <code><span class=typeGood>besøkte han oslo om sommeren</span><span class=typeMissed>.</span></code></div>'

def test_issue_28_disabled_separator() -> None:
    correct = 'Da pappa var ung, besøkte han oslo om sommeren.'
    given = 'Da pappa var ung, besøkte han oslo om sommeren'
    config = Config({
        "Separators": "",
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>Da pappa var ung, besøkte han oslo om sommeren</span><span class=typeMissed>.</span></code></div>'

def test_issue_28_missing_separator() -> None:
    correct = 'Da pappa var ung, besøkte han oslo om sommeren.'
    given = 'Da pappa var ung besøkte han oslo om sommeren'
    config = Config({
        "Ignored Characters": ",. ",
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>Da pappa var ung</span><span class=typeMissed>,</span><span class=typeGood> besøkte han oslo om sommeren</span><span class=typeMissed>.</span></code></div>'

def test_issue_31_slash_separator() -> None:
    correct = 'a,b / c,d'
    given = 'c,d/a,b'
    config = Config({
        "Separators": "/",
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>c,d</span></code> / <code><span class=typeGood>a,b</span></code></div>'

def test_issue_34_diff_algorithm_for_arrange_1() -> None:
    correct = "I'm travel(l)ing around the world., I travel around the world."
    given = 'i travel around the world'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>I travel around the world</span><span class=typeMissed>.</span></code>, <code><span class=typeMissed>I&#x27;m travel(l)ing around the world.</span></code></div>'

def test_issue_34_diff_algorithm_for_arrange_2() -> None:
    correct = "I travel around the world., I'm travel(l)ing around the world."
    given = 'i travel around the world'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>I travel around the world</span><span class=typeMissed>.</span></code>, <code><span class=typeMissed>I&#x27;m travel(l)ing around the world.</span></code></div>'

def test_issue_34_diff_algorithm_for_arrange_3() -> None:
    correct = "I'm travel(l)ing around the world., I travel around the world."
    given = "i'm traveling around the world"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>I&#x27;m travel</span><span class=typeMissed>(l)</span><span class=typeGood>ing around the world</span><span class=typeMissed>.</span></code>, <code><span class=typeMissed>I travel around the world.</span></code></div>'

def test_issue_34_diff_algorithm_for_arrange_4() -> None:
    correct = "I travel around the world., I'm travel(l)ing around the world."
    given = "i'm traveling around the world"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div id=typeans><code><span class=typeGood>I&#x27;m travel</span><span class=typeMissed>(l)</span><span class=typeGood>ing around the world</span><span class=typeMissed>.</span></code>, <code><span class=typeMissed>I travel around the world.</span></code></div>'
