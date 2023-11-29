from src import compare_answer_no_html

def test_no_missing():
    correct = 'test answer'
    given = 'test answer'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>test answer</span></code></div>'

def test_missing_space():
    correct = 'test answer'
    given = 'testanswer'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>test</span><span class=typeMissed> </span><span class=typeGood>answer</span></code></div>'

def test_missing_parentheses():
    correct = 'test (word) answer'
    given = 'testanswer'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>test</span><span class=typeMissed> (word) </span><span class=typeGood>answer</span></code></div>'

def test_missing_alternative_start():
    correct = 'test abc/def/ghi test'
    given = 'test abc test'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>test abc</span><span class=typeMissed>/def/ghi</span><span class=typeGood> test</span></code></div>'

def test_missing_alternative_middle():
    correct = 'test abc/def/ghi test'
    given = 'test def test'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>test </span><span class=typeMissed>abc/</span><span class=typeGood>def</span><span class=typeMissed>/ghi</span><span class=typeGood> test</span></code></div>'

def test_missing_alternative_not_middle():
    correct = 'test abc/def/ghi test'
    given = 'test abc/ghi test'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>test abc/</span><span class=typeMissed>def/</span><span class=typeGood>ghi test</span></code></div>'

def test_missing_alternative_end():
    correct = 'test abc/def/ghi test'
    given = 'test ghi test'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>test </span><span class=typeMissed>abc/def/</span><span class=typeGood>ghi test</span></code></div>'

def test_missing_alternative_all():
    correct = 'test abc/def/ghi test'
    given = 'test test'
    result = compare_answer_no_html(correct, given)
    assert 'typearrow' in result

def test_missing_alternative_start_with_brackets():
    correct = 'test abc/def/ghi (wx yz). test'
    given = 'test abc test'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>test abc</span><span class=typeMissed>/def/ghi (wx yz).</span><span class=typeGood> test</span></code></div>'

def test_missing_alternative_middle_with_brackets():
    correct = 'test abc/d(e)f/ghi test'
    given = 'test def test'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>test </span><span class=typeMissed>abc/</span><span class=typeGood>d</span><span class=typeMissed>(</span><span class=typeGood>e</span><span class=typeMissed>)</span><span class=typeGood>f</span><span class=typeMissed>/ghi</span><span class=typeGood> test</span></code></div>'

def test_missing_alternative_not_middle_with_brackets():
    correct = 'test abc/d[ wx yz ]f/ghi test'
    given = 'test abc/ghi test'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>test abc/</span><span class=typeMissed>d[ wx yz ]f/</span><span class=typeGood>ghi test</span></code></div>'

def test_missing_alternative_end_with_brackets():
    correct = 'test [wx yz]. abc/def/ghi test'
    given = 'test ghi test'
    result = compare_answer_no_html(correct, given)
    assert result == '<div><code id=typeans><span class=typeGood>test </span><span class=typeMissed>[wx yz]. abc/def/</span><span class=typeGood>ghi test</span></code></div>'
