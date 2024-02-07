import re

from .group import group_combining

def get_config_var(config, var_name: str, default_value):
    try:
        value = config[var_name]
    except:
        return default_value

    if type(value) is not type(default_value):
        return default_value

    return value

def lowercase_if_ignore_case(s: str, ignore_case: bool) -> str:
    return s.lower() if ignore_case else s

def get_equivalent_strings_config_var(config, var_name: str, default_value: list[str], ignore_case: bool) -> list[list[list[str]]]:
    return list(
        filter(
            lambda xs: len(xs) >= 2,
            (
                [
                    [
                        lowercase_if_ignore_case(ch, ignore_case)
                        for ch in group_combining(x)
                    ]
                    for x in xs
                    if x and type(x) is str
                ]
                for xs in get_config_var(config, var_name, default_value)
                if type(xs) is list
            )
        )
    )

class Config:
    def __init__(self, config = None):
        self.answer_choice_comments = get_config_var(config, 'Enable Answer Choice Comments [...]', False)
        self.answer_comments = get_config_var(config, 'Enable Answer Comments (...)', False)
        self.lenient_validation = get_config_var(config, 'Enable Lenient Validation', True)
        self.ignore_case = get_config_var(config, 'Ignore Case', True)
        self.ignore_separators_in_brackets = get_config_var(config, 'Ignore Separators in Brackets', True)

        self.ignored_characters = lowercase_if_ignore_case(get_config_var(config, 'Ignored Characters', ' .-'), self.ignore_case)
        self.equivalent_strings = get_equivalent_strings_config_var(config, 'Equivalent Strings', [], self.ignore_case)
        self.diff_lookbehind = max(1, max((len(x) for xs in self.equivalent_strings for x in xs), default=0))

        self.space_re = re.compile(r" +")

        self.bracket_start = '(['
        self.bracket_end = ')]'
        self.bracket_chars = self.bracket_start + self.bracket_end
        self.whitespace_chars = ' \t\r\n'
        self.keep_in_alternative_chars = self.whitespace_chars + self.bracket_chars
        self.junk_chars = self.ignored_characters.replace(' ', self.whitespace_chars) + self.bracket_chars
        self.junk_trans = {ord(ch): None for ch in self.junk_chars}

        self.allow_alternative_continue = "'-_"
