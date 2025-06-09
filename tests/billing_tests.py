import unittest
from unittest.mock import patch, MagicMock
from billing.billing_module import *
from db.methods import *
from db.db_module import connect_to_db
from pony.orm import db_session


class TestBilling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        connect_to_db()

    def setUp(self):
        # Очистка базы данных перед каждым тестом
        with db_session:
            Dialog.select().delete()
            Assistant.select().delete()

    def test_check_subscription(self):
        chat_id = "test_chat_1"
        api_key = "test_api_key"
        
        with db_session:
            create_dialog(chat_id, api_key)
            
            # Тест для бесплатной подписки
            self.assertTrue(check_subscription(chat_id, "free"))
            self.assertFalse(check_subscription(chat_id, "pro"))
            
            # Обновляем статус подписки
            update_dialog(chat_id, subscription_status="pro")
            
            # Тест для pro подписки
            self.assertTrue(check_subscription(chat_id, "pro"))
            self.assertTrue(check_subscription(chat_id, "free"))

    def test_is_enough_tokens(self):
        chat_id = "test_chat_2"
        api_key = "test_api_key"
        
        with db_session:
            create_dialog(chat_id, api_key)
            
            # Тест с достаточным количеством токенов
            self.assertTrue(is_enough_tokens(chat_id))
            
            # Тест с недостаточным количеством токенов
            # TODO: Добавить тест с недостаточным количеством токенов
            # Это потребует модификации функции is_enough_tokens для тестирования

    @patch('billing.billing_module.requests.post')
    def test_add_tokens(self, mock_post):
        # Настройка мока
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "tokens": 1000}
        mock_post.return_value = mock_response

        chat_id = "test_chat_3"
        api_key = "test_api_key"
        amount = 1000
        
        with db_session:
            create_dialog(chat_id, api_key)
            
            result = add_tokens(chat_id, amount)
            
            self.assertTrue(result["success"])
            self.assertEqual(result["tokens"], amount)

    @patch('billing.billing_module.requests.get')
    def test_get_balance(self, mock_get):
        # Настройка мока
        mock_response = MagicMock()
        mock_response.json.return_value = {"balance": 1000}
        mock_get.return_value = mock_response

        chat_id = "test_chat_4"
        api_key = "test_api_key"
        
        with db_session:
            create_dialog(chat_id, api_key)
            
            result = get_balance(chat_id)
            
            self.assertEqual(result["balance"], 1000)

    def test_update_subscription_status(self):
        chat_id = "test_chat_5"
        api_key = "test_api_key"
        
        with db_session:
            create_dialog(chat_id, api_key)
            
            update_subscription_status(chat_id, "pro")
            dialog = get_dialog(chat_id)
            self.assertEqual(dialog.subscription_status, "pro")
            
            update_subscription_status(chat_id, "free")
            dialog = get_dialog(chat_id)
            self.assertEqual(dialog.subscription_status, "free")


if __name__ == '__main__':
    unittest.main() 