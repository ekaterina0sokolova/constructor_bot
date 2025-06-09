import unittest
from unittest.mock import patch, MagicMock
from assistant.assistant_module import *
from db.methods import *
from db.db_module import connect_to_db
from pony.orm import db_session


class TestAssistant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        connect_to_db()

    def setUp(self):
        # Очистка базы данных перед каждым тестом
        with db_session:
            Dialog.select().delete()
            Assistant.select().delete()

    @patch('assistant.assistant_module.OpenAI')
    def test_create_assistant(self, mock_openai):
        # Настройка мока
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.beta.assistants.create.return_value = MagicMock(
            id="test_assistant_id",
            name="Test Assistant",
            instructions="Test instructions",
            model="gpt-4",
            tools=[],
            temperature=0.7,
            top_p=1.0
        )

        chat_id = "test_chat_1"
        api_key = "test_api_key"
        name = "Test Assistant"
        instructions = "Test instructions"

        with db_session:
            create_dialog(chat_id, api_key)
            result = create_assistant(chat_id, name, instructions)

            self.assertEqual(result.id, "test_assistant_id")
            self.assertEqual(result.name, name)
            self.assertEqual(result.instructions, instructions)

    @patch('assistant.assistant_module.OpenAI')
    def test_update_assistant(self, mock_openai):
        # Настройка мока
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.beta.assistants.update.return_value = MagicMock(
            id="test_assistant_id",
            name="Updated Assistant",
            instructions="Updated instructions"
        )

        chat_id = "test_chat_2"
        api_key = "test_api_key"
        assistant_id = "test_assistant_id"
        new_name = "Updated Assistant"
        new_instructions = "Updated instructions"

        with db_session:
            create_dialog(chat_id, api_key)
            create_db_assistant(assistant_id, chat_id, "test_thread")
            
            result = update_assistant(chat_id, assistant_id, name=new_name, instructions=new_instructions)
            
            self.assertEqual(result.name, new_name)
            self.assertEqual(result.instructions, new_instructions)

    @patch('assistant.assistant_module.OpenAI')
    def test_delete_assistant(self, mock_openai):
        # Настройка мока
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.beta.assistants.delete.return_value = MagicMock(
            id="test_assistant_id",
            deleted=True
        )

        chat_id = "test_chat_3"
        api_key = "test_api_key"
        assistant_id = "test_assistant_id"

        with db_session:
            create_dialog(chat_id, api_key)
            create_db_assistant(assistant_id, chat_id, "test_thread")
            
            result = delete_assistant(chat_id, assistant_id)
            
            self.assertTrue(result.deleted)
            with self.assertRaises(ValueError):
                get_db_assistant(assistant_id)

    @patch('assistant.assistant_module.OpenAI')
    def test_get_assistant(self, mock_openai):
        # Настройка мока
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.beta.assistants.retrieve.return_value = MagicMock(
            id="test_assistant_id",
            name="Test Assistant",
            instructions="Test instructions",
            model="gpt-4",
            tools=[],
            temperature=0.7,
            top_p=1.0
        )

        chat_id = "test_chat_4"
        api_key = "test_api_key"
        assistant_id = "test_assistant_id"

        with db_session:
            create_dialog(chat_id, api_key)
            create_db_assistant(assistant_id, chat_id, "test_thread")
            
            result = get_assistant(chat_id, assistant_id)
            
            self.assertEqual(result.id, assistant_id)
            self.assertEqual(result.name, "Test Assistant")
            self.assertEqual(result.instructions, "Test instructions")


if __name__ == '__main__':
    unittest.main() 