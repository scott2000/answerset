from src import compare_answer_no_html

def test_issue_2_alternative():
    correct = "be set in one's/my ways"
    given = 'be set in my ways'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>be set in </span><span class=typeMissed>one&#x27;s/</span><span class=typeGood>my ways</span></code></div>'

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
