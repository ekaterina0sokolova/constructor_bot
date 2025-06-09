import unittest
from locale_module import add_character_before_special
from storage_module import *


class TestModule(unittest.TestCase):
    def test_parse_dot_start(self):
        self.assertEqual(add_character_before_special('.ertyuj'), '\\.ertyuj')

    def test_parse_dot_end(self):
        self.assertEqual(add_character_before_special('ertyuj.'), 'ertyuj\\.')

    def test_parse_two_dots(self):
        self.assertEqual(add_character_before_special('ertyuj..'), 'ertyuj\\.\\.')

    def test_parse_string_with_only_special_chars(self):
        self.assertEqual(add_character_before_special('*_[]{}'), '\\*\\_\\[\\]\\{\\}')

    def test_parse_empty_string(self):
        self.assertEqual(add_character_before_special(''), '')

    def test_parse_string_with_nums(self):
        self.assertEqual(add_character_before_special('-3.5'), '\\-3\\.5')

    def test_create_new_dialog(self):
        create_dialog('1236')
        result = get_dialog('1236')

        if get_dialog('1236') is not None:
            self.assertRaises(ValueError)
        else:
            self.assertEqual(
                result,
                {
                    'user_id': '1236',
                    'confirmed': False,
                    'language': 'en',
                    'subscription_status': 'free',
                    'current_assistant_id': '',
                    'current_llm_id': 'llm_1',
                    'assistants_list': [],
                    'llm_list': [
                        "llm_1",
                        "llm_2",
                        "llm_3",
                        "llm_4"
                    ],
                    'save_context': 1,
                }
            )

    def test_get_new_dialog_info(self):
        dialog = get_dialog('1235')
        self.assertEqual(dialog['user_id'], '1235')
        self.assertEqual(dialog['language'], 'en')
        self.assertEqual(dialog['subscription_status'], 'free')
        self.assertEqual(dialog['current_assistant_id'], '')
        self.assertEqual(dialog['current_llm_id'], 'llm_1')
        self.assertEqual(dialog['assistants_list'], [])
        self.assertEqual(dialog['llm_list'], ["llm_1", "llm_2", "llm_3", "llm_4"])
        self.assertEqual(dialog['save_context'], 1)

    def test_change_new_dialog_info(self):
        dialog = get_dialog('1234')
        update_dialog(
            user_id=dialog['user_id'],
            language='ru',
            subscription_status='pro',
            current_llm_id='llm_2',
            save_context=0,
            assistants_list=["as_1"]
        )
        self.assertEqual(
            get_dialog('1234'),
            {
                'user_id': '1234',
                'confirmed': False,
                'language': 'ru',
                'subscription_status': 'pro',
                'current_assistant_id': '',
                'current_llm_id': 'llm_2',
                'assistants_list': ["as_1"],
                'llm_list': [
                    "llm_1",
                    "llm_2",
                    "llm_3",
                    "llm_4"
                ],
                'save_context': 0,
            }
        )


if __name__ == '__main__':
    unittest.main()
