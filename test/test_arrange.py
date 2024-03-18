from answerset.arrange import arrange
from answerset.config import Config

test_config = Config()

def test_arrange_empty() -> None:
    result = arrange(test_config, [], [])
    assert result == []

def test_arrange_given_empty() -> None:
    result = arrange(
        test_config,
        [],
        [('abc', '')],
    )
    expected = [
        (None, ('abc', '')),
    ]
    assert result == expected

def test_arrange_correct_empty() -> None:
    result = arrange(
        test_config,
        [('abc', '')],
        [],
    )
    expected = [
        (('abc', ''), None),
    ]
    assert result == expected

def test_arrange_one() -> None:
    result = arrange(
        test_config,
        [('abc', '')],
        [('abc', '')],
    )
    expected = [
        (('abc', ''), ('abc', '')),
    ]
    assert result == expected

def test_arrange_two() -> None:
    result = arrange(
        test_config,
        [('abc', ''), ('def', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        (('abc', ''), ('abc', '')),
        (('def', ''), ('def', '')),
    ]
    assert result == expected

def test_arrange_swap() -> None:
    result = arrange(
        test_config,
        [('def', ' [def given]'), ('abc', ' [abc given]')],
        [('abc', ' [abc correct]'), ('def', ' [def correct]')],
    )
    expected = [
        (('def', ' [def given]'), ('def', ' [def correct]')),
        (('abc', ' [abc given]'), ('abc', ' [abc correct]')),
    ]
    assert result == expected

def test_arrange_missing() -> None:
    result = arrange(
        test_config,
        [('def', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        (('def', ''), ('def', '')),
        (None, ('abc', '')),
    ]
    assert result == expected

def test_arrange_extra() -> None:
    result = arrange(
        test_config,
        [('abc', ''), ('def', '')],
        [('def', '')],
    )
    expected = [
        (('abc', ''), None),
        (('def', ''), ('def', '')),
    ]
    assert result == expected

def test_arrange_with_mistake_1() -> None:
    result = arrange(
        test_config,
        [('deff', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        (('deff', ''), ('def', '')),
        (None, ('abc', '')),
    ]
    assert result == expected

def test_arrange_with_mistake_2() -> None:
    result = arrange(
        test_config,
        [('eff', ''), ('ab', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        (('eff', ''), ('def', '')),
        (('ab', ''), ('abc', '')),
    ]
    assert result == expected

def test_arrange_with_mistake_3() -> None:
    result = arrange(
        test_config,
        [('def', ''), ('cab', '')],
        [('abc', '')],
    )
    expected = [
        (('def', ''), None),
        (('cab', ''), ('abc', '')),
    ]
    assert result == expected

def test_arrange_with_mistake_4() -> None:
    result = arrange(
        test_config,
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

def test_arrange_with_mistake_5() -> None:
    result = arrange(
        test_config,
        [('some answer', '')],
        [('some answer (but with a super long comment that is technically wrong but should not be penalized)', ''), ('other answer', '')],
    )
    expected = [
        (('some answer', ''), ('some answer (but with a super long comment that is technically wrong but should not be penalized)', '')),
        (None, ('other answer', '')),
    ]
    assert result == expected

def test_arrange_with_mistake_6() -> None:
    result = arrange(
        test_config,
        [('mouse', ''), ('cow', '')],
        [('dog', ''), ('cat', ''), ('mouse', ' [animal]')],
    )
    expected = [
        (('mouse', ''), ('mouse', ' [animal]')),
        (('cow', ''), ('cat', '')),
        (None, ('dog', '')),
    ]
    assert result == expected

def test_arrange_with_junk() -> None:
    result = arrange(
        test_config,
        [('some ------------------- answer', '')],
        [('------------------- answer', ''), ('some answer', '')],
    )
    expected = [
        (('some ------------------- answer', ''), ('some answer', '')),
        (None, ('------------------- answer', '')),
    ]
    assert result == expected

def test_arrange_with_only_junk() -> None:
    result = arrange(
        test_config,
        [('.-', '')],
        [('---', ''), ('-.-', ''), ('...', '')],
    )
    expected = [
        (('.-', ''), ('-.-', '')),
        (None, ('---', '')),
        (None, ('...', '')),
    ]
    assert result == expected
