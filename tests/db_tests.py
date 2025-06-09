import unittest
from db.db_module import connect_to_db
from db.methods import *
from db.models import Dialog, Assistant
from pony.orm import db_session


class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        connect_to_db()

    def setUp(self):
        # Очистка базы данных перед каждым тестом
        with db_session:
            Dialog.select().delete()
            Assistant.select().delete()

    def test_create_dialog(self):
        chat_id = "test_chat_1"
        api_key = "test_api_key"
        
        with db_session:
            result = create_dialog(chat_id, api_key)
            self.assertEqual(result, chat_id)
            
            dialog = get_dialog(chat_id)
            self.assertEqual(dialog.chat_id, chat_id)
            self.assertEqual(dialog.api_key, api_key)
            self.assertEqual(dialog.confirmed, False)
            self.assertEqual(dialog.language, 'en')
            self.assertEqual(dialog.subscription_status, 'free')

    def test_update_dialog(self):
        chat_id = "test_chat_2"
        api_key = "test_api_key"
        
        with db_session:
            create_dialog(chat_id, api_key)
            
            # Тест обновления языка
            update_dialog(chat_id, language='ru')
            dialog = get_dialog(chat_id)
            self.assertEqual(dialog.language, 'ru')
            
            # Тест обновления статуса подписки
            update_dialog(chat_id, subscription_status='pro')
            dialog = get_dialog(chat_id)
            self.assertEqual(dialog.subscription_status, 'pro')

    def test_create_assistant(self):
        chat_id = "test_chat_3"
        api_key = "test_api_key"
        assistant_id = "test_assistant_1"
        thread_id = "test_thread_1"
        
        with db_session:
            create_dialog(chat_id, api_key)
            result = create_db_assistant(assistant_id, chat_id, thread_id)
            
            self.assertEqual(result, assistant_id)
            assistant = get_db_assistant(assistant_id)
            self.assertEqual(assistant.assistant_id, assistant_id)
            self.assertEqual(assistant.thread_id, thread_id)

    def test_get_dialog_assistants(self):
        chat_id = "test_chat_4"
        api_key = "test_api_key"
        
        with db_session:
            create_dialog(chat_id, api_key)
            
            # Создаем несколько ассистентов
            assistant_ids = []
            for i in range(3):
                assistant_id = f"test_assistant_{i}"
                thread_id = f"test_thread_{i}"
                create_db_assistant(assistant_id, chat_id, thread_id)
                assistant_ids.append(assistant_id)
            
            # Проверяем получение списка ассистентов
            result = get_dialog_assistants_ids(chat_id)
            self.assertEqual(set(result), set(assistant_ids))

    def test_delete_assistant(self):
        chat_id = "test_chat_5"
        api_key = "test_api_key"
        assistant_id = "test_assistant_1"
        thread_id = "test_thread_1"
        
        with db_session:
            create_dialog(chat_id, api_key)
            create_db_assistant(assistant_id, chat_id, thread_id)
            
            # Проверяем удаление ассистента
            delete_db_assistant(assistant_id)
            with self.assertRaises(ValueError):
                get_db_assistant(assistant_id)


if __name__ == '__main__':
    unittest.main()
