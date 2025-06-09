from typing import Dict
import re

from data.RU_LOCALE import LEXICON_RU
from data.EN_LOCALE import LEXICON_EN


def add_character_before_special(string) -> str:
    # special_characters = ['_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    special_characters = ['!']

    for char in special_characters:
        string = string.replace(char, f'\{char}')

    return string


def add_lorem_text(string) -> str:
    return string+'\n\nLorem ipsum dolor sit amet\\, consectetur adipiscing elit\\, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua\\. Ut enim ad minim veniam\\, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat\\. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur\\. \n\nLorem ipsum dolor sit amet\\, consectetur adipiscing elit\\, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua\\. Ut enim ad minim veniam\\, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat\\. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur\\.'


def get_text(param: str, lang: str = 'ru', lexicons: dict = {}) -> str:
    ret: str = ""

    # form text based on language settings
    # in case of key is absent in the dictionary - print param`s name
    if lexicons == {}:
        if lang == 'ru':
            ret = LEXICON_RU.get(param, param)
        else:
            ret = LEXICON_EN.get(param, param)
    else:
        lexicon: Dict[str, str] = lexicons.get(lang.upper(), {})
        ret = lexicon.get(param, param)

    # ret = add_character_before_special(ret)

    # if not param.endswith('button'):
    #     ret = add_lorem_text(ret)

    return str(ret)
