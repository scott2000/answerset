import re

try:
    import aqt
    config = aqt.mw.addonManager.getConfig(__name__)
except:
    config = None

def get_config_var(var_name, default_value):
    try:
        value = config[var_name]
    except:
        return default_value

    if type(value) is not type(default_value):
        return default_value

    return value

answer_choice_comments = get_config_var('Enable Answer Choice Comments [...]', False)
answer_comments = get_config_var('Enable Answer Comments (...)', False)
lenient_validation = get_config_var('Enable Lenient Validation', True)
ignore_case = get_config_var('Ignore Case', True)
ignore_separators_in_brackets = get_config_var('Ignore Separators in Brackets', True)
ignored_characters = get_config_var('Ignored Characters', ' .-')

space_re = re.compile(r" +")

bracket_start = '(['
bracket_end = ')]'
bracket_chars = bracket_start + bracket_end
whitespace_chars = ' \t\r\n'
keep_in_alternative_chars = whitespace_chars + bracket_chars
junk_chars = ignored_characters.replace(' ', whitespace_chars) + bracket_chars
junk_trans = {ord(ch): None for ch in junk_chars}

allow_alternative_continue = "'-_"
