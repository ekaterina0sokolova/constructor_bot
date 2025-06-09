from typing import Text

from openai import OpenAI
# from assistant_config import OPENAI_TOKEN, PROXIES, ASSISTANT_ID
import time

from openai.lib.streaming import AssistantEventHandler

from auth.auth import get_api_key
from db.methods import get_dialog, update_dialog, update_db_assistant, get_db_assistant, create_db_assistant, \
    delete_db_assistant
from db.db_module import connect_to_db
import logging
from config import OPENAI_API_BASE_URL
from errors import InsufficientBalanceError


class StreamEventHandler(AssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.result_text = ""
        self.__stream = None

    def on_text_done(self, text: str) -> None:
        self.result_text += text

    def on_error(self):
        logging.error("Stream completion error in StreamEventHandler ", self)

    def get_result_text(self):
        return self.result_text


def create_openai_obj(api_key: str):
    try:
        client = OpenAI(api_key=api_key, base_url=OPENAI_API_BASE_URL)
        return client
    except Exception as e:
        logging.error("Failed to create OpenAI object", e)


def submit_message(assistant_id, thread_id, user_input, client):
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_input
    )

    stream_handler = StreamEventHandler()

    try:
        with client.beta.threads.runs.stream(
                thread_id=thread_id,
                assistant_id=assistant_id,
                event_handler=stream_handler
        ) as stream:
            stream.until_done()

        return stream_handler.result_text
    except Exception as e:
        # если код ошибки = 429, то у пользователя закончились токены - вызываем кастомную ошибку
        if hasattr(e, 'status_code') and e.status_code == 429:
            raise InsufficientBalanceError()
        else:
            raise e


def delete_context(api_key: str, assistant_id: str):
    client = create_openai_obj(api_key)

    assistant = get_db_assistant(assistant_id)
    thread_id = assistant.thread_id

    try:
        # вариант удаления контекста через создание нового треда
        client.beta.threads.delete(thread_id=thread_id)
        new_thread_id = client.beta.threads.create().id
        update_db_assistant(assistant_id=assistant_id, thread_id=new_thread_id)
    except Exception as e:
        raise e


def create_thread_and_run(user_input: str, client: OpenAI, assistant_id: str) -> str:
    assistant = get_db_assistant(assistant_id)

    try:
        thread = client.beta.threads.retrieve(thread_id=assistant.thread_id)
        text = submit_message(assistant_id, thread.id, user_input, client)
    except InsufficientBalanceError:
        raise InsufficientBalanceError()
        logging.info(f"User exceeded his current quota assistant_id={assistant_id}")
    except Exception as e:
        # check: нужно ли обновлять диалог (или ситуации, когда диалог есть, а треда нет - не должно быть?)
        thread = client.beta.threads.create()
        update_db_assistant(assistant_id=assistant_id, thread_id=thread.id)
        text = submit_message(assistant_id, thread.id, user_input, client)
        logging.warning("Created new thread for assistant_id=assistant_id, because of the Exception: ", e)

    return text


# создает тред и возвращает его id
def create_thread(chat_id: str) -> str:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    try:
        thread = client.beta.threads.create()
        return thread.id
    except Exception as e:
        raise ValueError(f"Failed to create thread chat_id={chat_id}", e)


# Удаляет ассистента OpenAI и тред, который к нему присоединен
def delete_assistant(chat_id, assistant_id) -> None:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    assistant = get_db_assistant(assistant_id)
    thread_id = assistant.thread_id

    try:
        delete_db_assistant(assistant_id)
        client.beta.assistants.delete(
            assistant_id=assistant_id
        )
        client.beta.threads.delete(
            thread_id=thread_id
        )
    except Exception as e:
        raise e


# Создет ассистента OpenAI, возвращает обект Asssistant
# создает новый тред для ассистента
# создает запись в БД
def create_assistant(chat_id, name: str, instructions: str, model: str = 'openai:gpt-4o-mini'):
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model=model,
        temperature=0.6,
        top_p=1,
    )

    thread_id = create_thread(chat_id)
    create_db_assistant(assistant.id, chat_id, thread_id=thread_id)

    return assistant


# ----------------------------------------- Изменение параметров ассистента ---------------------
def update_assistant_name(
        chat_id: str,
        assistant_id: str,
        name: str,
) -> None:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    try:
        client.beta.assistants.update(
            assistant_id=assistant_id,
            name=name,
        )
    except Exception as e:
        logging.error("Failed to update assistant name: ", e)


def update_assistant_description(
        chat_id: str,
        assistant_id: str,
        description: str,
) -> None:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    try:
        client.beta.assistants.update(
            assistant_id=assistant_id,
            description=description,
        )
    except Exception as e:
        logging.error(f"Failed to update assistant description chat_id={chat_id}", e)


def update_assistant_instructions(
        chat_id: str,
        assistant_id: str,
        instructions: str,
) -> None:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    try:
        client.beta.assistants.update(
            assistant_id=assistant_id,
            instructions=instructions,
        )
    except Exception as e:
        logging.error(f"Failed to update assistant instructions chat_id={chat_id}", e)


def update_assistant_llm_model(
        chat_id: str,
        assistant_id: str,
        llm_model: str,
) -> None:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    try:
        client.beta.assistants.update(
            assistant_id=assistant_id,
            model=llm_model,
        )
    except Exception as e:
        logging.error("Failed to update assistant llm_model: ", e)


def update_assistant_temperature(
        chat_id: str,
        assistant_id: str,
        temperature: float,
) -> None:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    try:
        client.beta.assistants.update(
            assistant_id=assistant_id,
            temperature=temperature,
        )
    except Exception as e:
        logging.error("Failed to update assistant temperature: ", e)


def update_assistant_top_p(
        chat_id: str,
        assistant_id: str,
        top_p: float,
) -> None:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    try:
        client.beta.assistants.update(
            assistant_id=assistant_id,
            top_p=top_p,
        )
    except Exception as e:
        logging.error("Failed to update assistant top_p: ", e)


def get_assistant(chat_id: str, assistant_id: str) -> str:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    # dialog = get_dialog(chat_id=chat_id)
    # assistant_id = dialog.current_assistant_id

    try:
        connect_to_db()
        assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)
    except Exception as e:
        raise e

    return assistant


def get_answer_from_assistant(chat_id: str, user_message: str) -> [int, str]:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    connect_to_db()
    dialog = get_dialog(chat_id=chat_id)

    assistant_id = dialog.current_assistant_id

    try:
        text = create_thread_and_run(user_message, client, assistant_id=assistant_id)
        status = 1
    except InsufficientBalanceError:
        text = "Недостаточно токенов.\nДля того, чтобы продолжить общение с ассистентом, пополните баланс в разделе 'Баланс и расходы'"
        status = 0

    return status, text


def update_assistant_storage_list(chat_id: str, storage_id_list: list):
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    assistant_id = get_dialog(chat_id).current_assistant_id

    try:
        client.beta.assistants.update(
            assistant_id=assistant_id,
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": storage_id_list
                }
            }
        )
    except Exception as e:
        logging.error("Failed to update assistant storage list: ", e)
        raise e


# возвращает список векторных хранилищ, которые использует ассистент
def get_assistant_storage_dict(chat_id: str) -> dict:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    current_assistant_id = get_dialog(chat_id).current_assistant_id
    assistant = client.beta.assistants.retrieve(assistant_id=current_assistant_id)
    assistant_storage_list = {}

    if assistant.tool_resources is not None:
        # получаем список векторных хранилищ, которые использует текущий ассистент
        assistant_storage_id_list = client.beta.assistants.retrieve(assistant_id=current_assistant_id).tool_resources.file_search.vector_store_ids

        # формируем словарь с данными о векторных хранилищах формата {id: name}
        for storage_id in assistant_storage_id_list:
            vector_storage = client.beta.vector_stores.retrieve(vector_store_id=storage_id)
            assistant_storage_list[vector_storage.id] = vector_storage.name
    else:
        assistant_storage_list = {}

    return assistant_storage_list


# возращает список всех векторных хранилищ пользователя
def get_all_user_storage_list(chat_id: str) -> list:
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    try:
        vector_stores = client.beta.vector_stores.list()
        vector_stores_list = vector_stores.data
    except Exception as e:
        logging.error(f"Failed to get vector storage list chat_id={chat_id}", exc_info=e)
        raise e

    return vector_stores_list


def create_vector_storage(chat_id: str, storage_name: str, file_paths: list):
    api_key = get_api_key(chat_id)[1]["api_key"]
    client = create_openai_obj(api_key)

    # информация о загруженных файлах: {id: name}
    uploaded_files = {}

    for file_path in file_paths:
        try:
            with open(file_path, "rb") as f:
                file = client.files.create(
                    file=f,
                    purpose="assistants",
                )
                uploaded_files[file.id] = file.filename
        except Exception as e:
            logging.error(f"Failed to create file {file_path} chat_id={chat_id}", exc_info=e)
            raise

    try:
        client.beta.vector_stores.create(
            name=storage_name,
            file_ids=list(uploaded_files.keys())
        )
    except Exception as e:
        logging.error(f"Failed to create vector storage chat_id={chat_id}", exc_info=e)
        raise
