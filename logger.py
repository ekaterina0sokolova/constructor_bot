import logging
from datetime import datetime
import os
import json


# log_dir = 'logs'
# if not os.path.exists(log_dir):
#     os.makedirs(log_dir)

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(funcName)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# Функция для логирования действий пользователей
# def log_user_action(chat_id, action):
#     user_log_file = os.path.join(log_dir, f'user_{chat_id}.json')
#     log_entry = {
#         'chat_id': chat_id,
#         'action': action,
#         'timestamp': datetime.now().isoformat()
#     }
#
#     # Запись лога в JSON формате
#     if os.path.exists(user_log_file):
#         with open(user_log_file, 'r+', encoding='utf-8') as f:
#             try:
#                 data = json.load(f)
#                 data.append(log_entry)
#                 f.seek(0)  # Переместить курсор в начало файла
#                 json.dump(data, f, indent=4,  ensure_ascii=False)
#             except json.JSONDecodeError:
#                 # Если файл пуст или не может быть прочитан, создаем новый список
#                 f.seek(0)
#                 json.dump([log_entry], f, indent=4,  ensure_ascii=False)
#     else:
#         with open(user_log_file, 'w', encoding='utf-8') as f:
#             json.dump([log_entry], f, indent=4,  ensure_ascii=False)
