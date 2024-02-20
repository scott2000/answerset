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

def test_equivalent_strings_ignore_case_unicode():
    correct = 'xß'
    given = 'y'
    config = Config({
        "Equivalent Strings": [
            ["xß", "y"],
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

def test_equivalent_strings_normalization_1():
    correct = '\u212B'
    given = 'A'
    config = Config({
        "Equivalent Strings": [
            ["A", "A\u030A"]
        ],
    })
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' not in result

def test_equivalent_strings_normalization_2():
    correct = 'A\u030A'
    given = 'A'
    config = Config({
        "Equivalent Strings": [
            ["A", "\u212B"]
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

def test_ignore_case_unicode():
    correct = 'xßy'
    given = 'xssy'
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

def test_ignored_characters_normalization_1():
    correct = 'test \u212B'
    given = 'test'
    config = Config({
        "Ignored Characters": "A\u030A ",
    })
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' not in result

def test_ignored_characters_normalization_2():
    correct = 'test A\u030A'
    given = 'test'
    config = Config({
        "Ignore Case": False,
        "Ignored Characters": "\u212B ",
    })
    result = compare_answer_no_html(config, correct, given)
    assert 'typearrow' not in result
