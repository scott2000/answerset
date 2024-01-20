from answerset import compare_answer_no_html

def test_issue_2_alternative():
    correct = "be set in one's/my ways"
    given = 'be set in my ways'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>be set in </span><span class=typeMissed>one&#x27;s/</span><span class=typeGood>my ways</span></code></div>'

def test_issue_2_alternative_in_brackets_first():
    correct = "There's no need to hurry - we've got [a lot of/plenty of] time."
    given = "There's no need to hurry - we've got a lot of time."
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>There&#x27;s no need to hurry - we&#x27;ve got </span><span class=typeMissed>[</span><span class=typeGood>a lot of</span><span class=typeMissed>/plenty of]</span><span class=typeGood> time.</span></code></div>'

def test_issue_2_alternative_in_brackets_second():
    correct = "There's no need to hurry - we've got [a lot of/plenty of] time."
    given = "There's no need to hurry - we've got plenty of time."
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>There&#x27;s no need to hurry - we&#x27;ve got </span><span class=typeMissed>[a lot of/</span><span class=typeGood>plenty of</span><span class=typeMissed>]</span><span class=typeGood> time.</span></code></div>'

def test_issue_3_starting():
    correct = 'start(ing)'
    given = 'start'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>start</span><span class=typeMissed>(ing)</span></code></div>'

def test_issue_4_period_after_bracket():
    correct = "They're coming at [time]."
    given = "They're coming at"
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>They&#x27;re coming at</span><span class=typeMissed> [time].</span></code></div>'

def test_issue_4_periods_at_end():
    correct = 'en/et favoritt...'
    given = 'en favoritt'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>en</span><span class=typeMissed>/et</span><span class=typeGood> favoritt</span><span class=typeMissed>...</span></code></div>'

def test_issue_4_periods_in_middle():
    correct = 'ser ... på'
    given = 'ser på'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>ser </span><span class=typeMissed>... </span><span class=typeGood>på</span></code></div>'

def test_issue_5_period_after_alternative():
    correct = 'Det er X i Yen/Ya.'
    given = 'Det er X i Yen'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>Det er X i Yen</span><span class=typeMissed>/Ya.</span></code></div>'

def test_issue_10_many_missing_chars():
    correct = 'kler på meg/deg/seg/oss, Xen'
    given = 'kler på meg'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>kler på meg</span><span class=typeMissed>/deg/seg/oss</span></code>, <code id=typeans><span class=typeMissed>Xen</span></code></div>'

def test_issue_10_separators_in_brackets():
    correct = 'kler på (meg/deg/seg/oss, Xen, ...)'
    given = 'kler på (meg, Xen, ...)'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>kler på (meg</span><span class=typeMissed>/deg/seg/oss</span><span class=typeGood>, Xen, ...)</span></code></div>'

def test_issue_13_alternative_in_bracket_in_word_first():
    correct = 'tar en (master/bachelor)grad i X'
    given = 'tar en mastergrad i X'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>tar en </span><span class=typeMissed>(</span><span class=typeGood>master</span><span class=typeMissed>/bachelor)</span><span class=typeGood>grad i X</span></code></div>'

def test_issue_13_alternative_in_bracket_in_word_second():
    correct = 'tar en (master/bachelor)grad i X'
    given = 'tar en bachelorgrad i X'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>tar en </span><span class=typeMissed>(master/</span><span class=typeGood>bachelor</span><span class=typeMissed>)</span><span class=typeGood>grad i X</span></code></div>'

def test_issue_13_alternative_in_bracket_in_word_both():
    correct = 'tar en (master/bachelor)grad i X'
    given = 'tar en master/bachelorgrad i X'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>tar en </span><span class=typeMissed>(</span><span class=typeGood>master/bachelor</span><span class=typeMissed>)</span><span class=typeGood>grad i X</span></code></div>'

def test_issue_13_alternative_in_bracket_in_word_neither():
    correct = 'tar en (master/bachelor)grad i X'
    given = 'tar en grad i X'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>tar en </span><span class=typeMissed>(master/bachelor)</span><span class=typeGood>grad i X</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_1():
    correct = 'point(ing/s) (at)'
    given = 'pointing at'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>point</span><span class=typeMissed>(</span><span class=typeGood>ing</span><span class=typeMissed>/s) (</span><span class=typeGood>at</span><span class=typeMissed>)</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_2():
    correct = 'point(ing/s) (at)'
    given = 'pointing'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>point</span><span class=typeMissed>(</span><span class=typeGood>ing</span><span class=typeMissed>/s) (at)</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_3():
    correct = 'point(ing/s) (at)'
    given = 'points at'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>point</span><span class=typeMissed>(ing/</span><span class=typeGood>s</span><span class=typeMissed>) (</span><span class=typeGood>at</span><span class=typeMissed>)</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_4():
    correct = 'point(ing/s) (at)'
    given = 'points'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>point</span><span class=typeMissed>(ing/</span><span class=typeGood>s</span><span class=typeMissed>) (at)</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_5():
    correct = 'point(ing/s) (at)'
    given = 'point at'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>point</span><span class=typeMissed>(ing/s) (</span><span class=typeGood>at</span><span class=typeMissed>)</span></code></div>'

def test_issue_16_adjacent_bracketed_alternatives_6():
    correct = 'point(ing/s) (at)'
    given = 'point'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>point</span><span class=typeMissed>(ing/s) (at)</span></code></div>'

def test_issue_18_overlapping_alternatives_1():
    correct = 'apprenticeship as a/an X'
    given = 'apprenticeship as a X'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>apprenticeship as a</span><span class=typeMissed>/an</span><span class=typeGood> X</span></code></div>'

def test_issue_18_overlapping_alternatives_2():
    correct = 'apprenticeship as a/an X'
    given = 'apprenticeship as an X'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>apprenticeship as </span><span class=typeMissed>a/</span><span class=typeGood>an X</span></code></div>'

def test_issue_18_overlapping_alternatives_3():
    correct = 'apprenticeship as an/a X'
    given = 'apprenticeship as an X'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>apprenticeship as an</span><span class=typeMissed>/a</span><span class=typeGood> X</span></code></div>'

def test_issue_18_overlapping_alternatives_4():
    correct = 'start/starting'
    given = 'start'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>start</span><span class=typeMissed>/starting</span></code></div>'

def test_issue_18_overlapping_alternatives_5():
    correct = 'start/starting'
    given = 'starting'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeMissed>start/</span><span class=typeGood>starting</span></code></div>'
