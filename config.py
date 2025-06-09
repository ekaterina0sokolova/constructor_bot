import os
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    print("no .env file found. using to environment variables")

BOT_TOKEN = os.getenv("BOT_TOKEN")
TEST_BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT")

# SERVER_PORT = os.getenv("SERVER_PORT")

# переменные для отслеживания состояния диалога
ASSISTANT_NAME, \
    ASSISTANT_INSTRUCTIONS, \
    NEW_ASSISTANT_NAME, \
    NEW_ASSISTANT_DESCRIPTION, \
    NEW_ASSISTANT_INSTRUCTIONS, \
    NEW_ASSISTANT_KNOWLEDGE_BASE, \
    NEW_ASSISTANT_TOP_P, \
    NEW_ASSISTANT_TEMPERATURE, \
    NEW_ASSISTANT_TOOLS, \
    CONFIRM_ASSISTANT_DELETION, \
    VECTOR_STORE_NAME, \
    VECTOR_STORE_DATA, \
    VECTOR_STORE_DONE = range(13)

DATABASE_URL = os.getenv("DATABASE_URL")

JWT_SECRET = os.getenv("JWT_SECRET")
BACKEND_URL = os.getenv("BACKEND_URL")
OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL")

MAX_ASSISTANT_CNT = 5
