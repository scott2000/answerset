from typing import Optional, Union

from answerset.arrange import UnmatchedChoice, arrange
from answerset.config import Config
from answerset.diff import Choice, ChoicePair

test_config = Config()

def to_basic_choices(pairs: list[Union[ChoicePair, UnmatchedChoice]]) -> list[Union[tuple[str, Choice], UnmatchedChoice]]:
    return [
        (''.join(pair.given), (''.join(pair.correct), pair.correct_comment))
        if isinstance(pair, ChoicePair)
        else pair
        for pair in pairs
    ]

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
        UnmatchedChoice(True, ('abc', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_correct_empty() -> None:
    result = arrange(
        test_config,
        [('abc', '')],
        [],
    )
    expected = [
        UnmatchedChoice(False, ('abc', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_one() -> None:
    result = arrange(
        test_config,
        [('abc', '')],
        [('abc', '')],
    )
    expected = [
        ('abc', ('abc', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_two() -> None:
    result = arrange(
        test_config,
        [('abc', ''), ('def', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        ('abc', ('abc', '')),
        ('def', ('def', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_swap() -> None:
    result = arrange(
        test_config,
        [('def', ' [def given]'), ('abc', ' [abc given]')],
        [('abc', ' [abc correct]'), ('def', ' [def correct]')],
    )
    expected = [
        ('def [def given]', ('def [def correct]', '')),
        ('abc [abc given]', ('abc [abc correct]', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_missing() -> None:
    result = arrange(
        test_config,
        [('def', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        ('def', ('def', '')),
        UnmatchedChoice(True, ('abc', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_extra() -> None:
    result = arrange(
        test_config,
        [('abc', ''), ('def', '')],
        [('def', '')],
    )
    expected = [
        UnmatchedChoice(False, ('abc', '')),
        ('def', ('def', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_with_mistake_1() -> None:
    result = arrange(
        test_config,
        [('deff', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        ('deff', ('def', '')),
        UnmatchedChoice(True, ('abc', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_with_mistake_2() -> None:
    result = arrange(
        test_config,
        [('eff', ''), ('ab', '')],
        [('abc', ''), ('def', '')],
    )
    expected = [
        ('eff', ('def', '')),
        ('ab', ('abc', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_with_mistake_3() -> None:
    result = arrange(
        test_config,
        [('def', ''), ('cab', '')],
        [('abc', '')],
    )
    expected = [
        UnmatchedChoice(False, ('def', '')),
        ('cab', ('abc', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_with_mistake_4() -> None:
    result = arrange(
        test_config,
        [('fat', ''), ('house', ''), ('horse', ''), ('cot', '')],
        [('dog', ''), ('cat', ''), ('mouse', '')],
    )
    expected = [
        UnmatchedChoice(False, ('fat', '')),
        ('house', ('mouse', '')),
        ('horse', ('dog', '')),
        ('cot', ('cat', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_with_mistake_5() -> None:
    result = arrange(
        test_config,
        [('some answer', '')],
        [('some answer (but with a super long comment that is technically wrong but should not be penalized)', ''), ('other answer', '')],
    )
    expected = [
        ('some answer', ('some answer (but with a super long comment that is technically wrong but should not be penalized)', '')),
        UnmatchedChoice(True, ('other answer', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_with_mistake_6() -> None:
    result = arrange(
        test_config,
        [('mouse', ''), ('cow', '')],
        [('dog', ''), ('cat', ''), ('mouse', ' [animal]')],
    )
    expected = [
        ('mouse', ('mouse', ' [animal]')),
        ('cow', ('cat', '')),
        UnmatchedChoice(True, ('dog', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_with_junk() -> None:
    result = arrange(
        test_config,
        [('some answer', '')],
        [('answer', ''), ('some ------------------- answer', '')],
    )
    expected = [
        ('some answer', ('some ------------------- answer', '')),
        UnmatchedChoice(True, ('answer', '')),
    ]
    assert to_basic_choices(result) == expected

def test_arrange_with_only_junk() -> None:
    result = arrange(
        test_config,
        [('.-', '')],
        [('---', ''), ('-.-', ''), ('...', '')],
    )
    expected = [
        ('.-', ('-.-', '')),
        UnmatchedChoice(True, ('---', '')),
        UnmatchedChoice(True, ('...', '')),
    ]
    assert to_basic_choices(result) == expected
