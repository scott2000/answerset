from answerset import compare_answer_no_html
from answerset.config import Config

def test_missing_space_no_lenient_validation():
    correct = 'test answer'
    given = 'testanswer'
    config = Config({
        "Enable Lenient Validation": False,
    })
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' in result

def test_missing_parentheses_no_lenient_validation():
    correct = 'test (word) answer'
    given = 'testanswer'
    config = Config({
        "Enable Lenient Validation": False,
    })
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' in result

def test_missing_alternative_no_lenient_validation():
    correct = 'test abc/def/ghi test'
    given = 'test def test'
    config = Config({
        "Enable Lenient Validation": False,
    })
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' in result

def test_equivalent_strings_ignore_case():
    correct = 'dog and moose'
    given = 'CAT and MOUSE'
    config = Config({
        "Equivalent Strings": [
            ["DOG", "cow", "cat"],
            ["mouse", "MOOSE"]
        ],
    })
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' not in result

def test_equivalent_strings_no_ignore_case():
    correct = 'dog and moose'
    given = 'CAT and MOUSE'
    config = Config({
        "Equivalent Strings": [
            ["dog", "cow", "CAT"],
            ["MOUSE", "moose"]
        ],
        "Ignore Case": False,
    })
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' not in result

def test_ignore_case():
    correct = 'I saw him'
    given = 'i saw Him'
    config = Config()
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' not in result

def test_no_ignore_case():
    correct = 'I saw him'
    given = 'i saw Him'
    config = Config({
        "Ignore Case": False,
    })
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' in result

def test_ignore_separators_in_brackets():
    correct = '(abc, def)'
    given = '(def, abc)'
    config = Config()
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' in result

def test_no_ignore_separators_in_brackets():
    correct = '(abc, def)'
    given = 'def, abc'
    config = Config({
        "Ignore Separators in Brackets": False,
    })
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' not in result

def test_missing_space_not_ignored():
    correct = 'test answer'
    given = 'testanswer'
    config = Config({
        "Ignored Characters": "",
    })
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' in result
