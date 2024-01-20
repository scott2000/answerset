from answerset import compare_answer_no_html

def test_doc_first_example():
    correct = 'depart, go, leave'
    given = 'leave, go'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>leave</span></code>, <code id=typeans><span class=typeGood>go</span></code>, <code id=typeans><span class=typeMissed>depart</span></code></div>'

def test_doc_indic_scripts():
    correct = 'திரும்பு'
    given = 'திரமபு'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>தி</span><span class=typeBad>ரம</span><span class=typeGood>பு</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>தி</span><span class=typeMissed>ரும்</span><span class=typeGood>பு</span></code></div>'

def test_doc_semicolon():
    correct = 'a, b, c; d, e, f'
    given = 'a, b, c'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>a, b, c</span></code>; <code id=typeans><span class=typeMissed>d, e, f</span></code></div>'

def test_doc_lenient_validation_missing_hyphen_period():
    correct = 'We co-operated.'
    given = 'We cooperated'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>We co</span><span class=typeMissed>-</span><span class=typeGood>operated</span><span class=typeMissed>.</span></code></div>'

def test_doc_lenient_validation_missing_paren_text():
    correct = 'start(ing)'
    given = 'start'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>start</span><span class=typeMissed>(ing)</span></code></div>'

def test_doc_lenient_validation_missing_parens():
    correct = 'start(ing)'
    given = 'starting'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>start</span><span class=typeMissed>(</span><span class=typeGood>ing</span><span class=typeMissed>)</span></code></div>'

def test_doc_lenient_validation_missing_alternative():
    correct = "set in one's/my ways"
    given = 'set in my ways'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>set in </span><span class=typeMissed>one&#x27;s/</span><span class=typeGood>my ways</span></code></div>'
