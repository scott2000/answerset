from answerset import compare_answer_no_html
from answerset.config import Config

test_config = Config()

def test_doc_first_example():
    correct = 'depart, go, leave'
    given = 'leave, go'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>leave</span></code>, <code id=typeans><span class=typeGood>go</span></code>, <code id=typeans><span class=typeMissed>depart</span></code></div>'

def test_doc_indic_scripts():
    correct = 'திரும்பு'
    given = 'திரமபு'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>தி</span><span class=typeBad>ரம</span><span class=typeGood>பு</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>தி</span><span class=typeMissed>ரும்</span><span class=typeGood>பு</span></code></div>'

def test_doc_semicolon():
    correct = 'a, b, c; d, e, f'
    given = 'a, b, c'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>a, b, c</span></code>; <code id=typeans><span class=typeMissed>d, e, f</span></code></div>'

def test_doc_lenient_validation_missing_hyphen_period():
    correct = 'We co-operated.'
    given = 'We cooperated'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>We co</span><span class=typeMissed>-</span><span class=typeGood>operated</span><span class=typeMissed>.</span></code></div>'

def test_doc_lenient_validation_missing_paren_text():
    correct = 'start(ing)'
    given = 'start'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>start</span><span class=typeMissed>(ing)</span></code></div>'

def test_doc_lenient_validation_missing_parens():
    correct = 'start(ing)'
    given = 'starting'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>start</span><span class=typeMissed>(</span><span class=typeGood>ing</span><span class=typeMissed>)</span></code></div>'

def test_doc_lenient_validation_missing_alternative():
    correct = "set in one's/my ways"
    given = 'set in my ways'
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>set in </span><span class=typeMissed>one&#x27;s/</span><span class=typeGood>my ways</span></code></div>'

def test_doc_lenient_validation_missing_alternative_with_spaces():
    correct = "we've got [a lot of/plenty of] time"
    given = "we've got a lot of time"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>we&#x27;ve got </span><span class=typeMissed>[</span><span class=typeGood>a lot of</span><span class=typeMissed>/plenty of]</span><span class=typeGood> time</span></code></div>'

def test_doc_lenient_validation_missing_alternative_bracket():
    correct = "we've got [a lot of/plenty of] time"
    given = "we've got time"
    result = compare_answer_no_html(test_config, correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>we&#x27;ve got </span><span class=typeMissed>[a lot of/plenty of] </span><span class=typeGood>time</span></code></div>'

def test_doc_answer_choice_comments():
    correct = 'dog, cat, mouse [animal]'
    given = 'mouse, cow'
    config = Config({
        "Enable Answer Choice Comments [...]": True,
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>mouse</span></code>, <code id=typeans><span class=typeGood>c</span><span class=typeBad>ow</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>mouse</span></code> [animal]<code id=typeans></code>, <code id=typeans><span class=typeGood>c</span><span class=typeMissed>at</span></code>, <code id=typeans><span class=typeMissed>dog</span></code></div>'

def test_doc_answer_comments():
    correct = 'dog, cat, mouse (animals)'
    given = 'mouse, cow'
    config = Config({
        "Enable Answer Comments (...)": True,
    })
    result = compare_answer_no_html(config, correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>mouse</span></code>, <code id=typeans><span class=typeGood>c</span><span class=typeBad>ow</span><br><span id=typearrow>&darr;</span><br><span class=typeGood>mouse</span></code>, <code id=typeans><span class=typeGood>c</span><span class=typeMissed>at</span></code>, <code id=typeans><span class=typeMissed>dog</span></code> (animals)<code id=typeans></code></div>'
