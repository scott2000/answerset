from answerset.arrange import arrange

def test_arrange_empty():
    result = arrange([], [])
    assert result == []

def test_arrange_given_empty():
    result = arrange(
        [],
        [('abc', '')],
    )
    expected = [
        (None, ('abc', '')),
    ]
    assert result == expected

def test_arrange_correct_empty():
    result = arrange(
        [('abc', '')],
        [],
    )
    expected = [
        (('abc', ''), None),
    ]
    assert result == expected

def test_arrange_one():
    result = arrange(
        [('abc', '')],
        [('abc', '')],
    )
    expected = [
        (('abc', ''), ('abc', '')),
    ]
    assert result == expected

def test_arrange_two():
    result = arrange(
        [('abc', ''), ('def', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        (('abc', ''), ('abc', '')),
        (('def', ''), ('def', '')),
    ]
    assert result == expected

def test_arrange_swap():
    result = arrange(
        [('def', ' [def given]'), ('abc', ' [abc given]')],
        [('abc', ' [abc correct]'), ('def', ' [def correct]')],
    )
    expected = [
        (('def', ' [def given]'), ('def', ' [def correct]')),
        (('abc', ' [abc given]'), ('abc', ' [abc correct]')),
    ]
    assert result == expected

def test_arrange_missing():
    result = arrange(
        [('def', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        (('def', ''), ('def', '')),
        (None, ('abc', '')),
    ]
    assert result == expected

def test_arrange_extra():
    result = arrange(
        [('abc', ''), ('def', '')],
        [('def', '')],
    )
    expected = [
        (('abc', ''), None),
        (('def', ''), ('def', '')),
    ]
    assert result == expected

def test_arrange_with_mistake_1():
    result = arrange(
        [('deff', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        (('deff', ''), ('def', '')),
        (None, ('abc', '')),
    ]
    assert result == expected

def test_arrange_with_mistake_2():
    result = arrange(
        [('eff', ''), ('ab', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        (('eff', ''), ('def', '')),
        (('ab', ''), ('abc', '')),
    ]
    assert result == expected

def test_arrange_with_mistake_3():
    result = arrange(
        [('def', ''), ('cab', '')],
        [('abc', '')],
    )
    expected = [
        (('def', ''), None),
        (('cab', ''), ('abc', '')),
    ]
    assert result == expected

def test_arrange_with_mistake_3():
    result = arrange(
        [('fat', ''), ('house', ''), ('horse', ''), ('cot', '')],
        [('dog', ''), ('cat', ''), ('mouse', '')],
    )
    expected = [
        (('fat', ''), None),
        (('house', ''), ('mouse', '')),
        (('horse', ''), ('dog', '')),
        (('cot', ''), ('cat', '')),
    ]
    assert result == expected

def test_arrange_with_mistake_4():
    result = arrange(
        [('some answer', '')],
        [('some answer (but with a super long comment that is technically wrong but should not be penalized)', ''), ('other answer', '')],
    )
    expected = [
        (('some answer', ''), ('some answer (but with a super long comment that is technically wrong but should not be penalized)', '')),
        (None, ('other answer', '')),
    ]
    assert result == expected

def test_arrange_with_mistake_5():
    result = arrange(
        [('mouse', ''), ('cow', '')],
        [('dog', ''), ('cat', ''), ('mouse', ' [animal]')],
    )
    expected = [
        (('mouse', ''), ('mouse', ' [animal]')),
        (('cow', ''), ('cat', '')),
        (None, ('dog', '')),
    ]
    assert result == expected

def test_arrange_with_junk():
    result = arrange(
        [('some ------------------- answer', '')],
        [('------------------- answer', ''), ('some answer', '')],
    )
    expected = [
        (('some ------------------- answer', ''), ('some answer', '')),
        (None, ('------------------- answer', '')),
    ]
    assert result == expected

def test_arrange_with_only_junk():
    result = arrange(
        [('.-', '')],
        [('---', ''), ('-.-', ''), ('...', '')],
    )
    expected = [
        (('.-', ''), ('-.-', '')),
        (None, ('---', '')),
        (None, ('...', '')),
    ]
    assert result == expected
