from pony.orm import *
from db.models import *
import logging
from db.db_module import connect_to_db, db
from openai import OpenAI


# ----------------------------- Dialog ----------------------------------
@db_session
def create_dialog(chat_id, api_key) -> str:
    # TODO white list check
    try:
        # check if dialog with chat_id exists in DB
        chat_id = get_dialog(chat_id).chat_id
        logging.warning(f"Tried to create dialog {chat_id} that already exists")
        return chat_id
    except:
        # get available llm list, creating new dialog, returning dialog chat_id
        current_llm = 'openai:gpt-4o-mini'


        dialog = Dialog(
            chat_id=chat_id,
            confirmed=False,
            language='en',
            subscription_status='free',
            current_assistant_id='',
            current_llm=current_llm,
            save_context=True,
            api_key=api_key,
        )
        db.commit()
        return dialog.chat_id


@db_session
def get_dialog(chat_id) -> Dialog:
    dialog = Dialog.get(chat_id=chat_id)

    if dialog is None:
        raise ValueError(f"Dialog with id {chat_id} not found.")

    return dialog


@db_session
def update_dialog(chat_id: str, language=None, confirmed=None, subscription_status=None, current_assistant_id=None,
                  current_llm=None, save_context=None) -> bool:
    try:
        dialog = get_dialog(chat_id=chat_id)
    except Exception as e:
        logging.error(f"Failed to get dialog {chat_id} when updating dialog", e)
        return False

    if language is not None:
        dialog.language = language
    if confirmed is not None:
        dialog.confirmed = confirmed
    if subscription_status is not None:
        dialog.subscription_status = subscription_status
        # if current_assistant_id is not None:
        # check if assistant with assistant_id exists in DB
        try:
            assistant = get_db_assistant(assistant_id=current_assistant_id)
            dialog.current_assistant_id = assistant.assistant_id
        except Exception as e:
            logging.error("Failed to set current_assistant_id in update_dialog", e)
    if current_assistant_id is not None:
        dialog.current_assistant_id = current_assistant_id
    if current_llm is not None:
        # check if llm with current_llm exists in DB
        try:
            dialog.current_llm = current_llm
        except Exception as e:
            logging.error("Failed to set current_llm in update_dialog", e)
    if save_context is not None:
        dialog.save_context = save_context

    return True


@db_session
def get_dialog_language(chat_id) -> Dialog.language:
    dialog = Dialog.get(chat_id=chat_id)

    if dialog is None:
        raise ValueError(f"Dialog with id {chat_id} not found.")

    # return dialog.language
    return 'ru'


@db_session
def get_dialog_subscription(chat_id) -> str:
    dialog = Dialog.get(chat_id=chat_id)

    if dialog is None:
        raise ValueError(f"Dialog with id {chat_id} not found.")

    return dialog.subscription_status


# Returns list of llms names
# @db_session
# def get_dialog_llms_names(chat_id) -> list:
#     dialog = Dialog.get(chat_id=chat_id)
#
#     if dialog is None:
#         raise ValueError(f"Dialog with id {chat_id} not found.")
#
#     llm_names = []
#     for llm in list(dialog.llms):
#         llm_names.append(llm.name)
#
#     return llm_names



# Returns list of assistants ids
@db_session
def get_dialog_assistants_ids(chat_id) -> list():
    dialog = Dialog.get(chat_id=chat_id)

    if dialog is None:
        raise ValueError(f"Dialog with id {chat_id} not found.")

    assistants_ids = []
    assistants = list(dialog.assistants)

    for assistant in assistants:
        assistants_ids.append(assistant.assistant_id)

    return assistants_ids


@db_session
def delete_dialog(chat_id):
    pass


# --------------------------- Assistant -------------------------
@db_session
def create_db_assistant(assistant_id, chat_id, thread_id: str, llm='openai:gpt-4o-mini') -> str:
    try:
        dialog = get_dialog(chat_id=chat_id)
    except Exception as e:
        logging.error("Failed to get dialog/llm when creating assistant in db", e)

    # check if assistant with assistant_id exists
    try:
        thread_id
        assistant_id = get_db_assistant(assistant_id=assistant_id).assistant_id
        logging.warning(f"Tried to create assistant {assistant_id} that already exists")
        return assistant_id
    except:
        # creating new assistant
        assistant = Assistant(
            assistant_id=assistant_id,
            dialog=dialog,
            llm=llm,
            thread_id=thread_id,
        )
        db.commit()
        return assistant.assistant_id


@db_session
def update_db_assistant(assistant_id: str, llm: str=None, thread_id: str=None) -> str:
    # check if assistant with assistant_id exists
    try:
        assistant = get_db_assistant(assistant_id=assistant_id)

        if llm is not None:
            assistant.llm = llm
        if thread_id is not None:
            assistant.thread_id = thread_id
    except Exception as e:
        raise Warning("Failed to update assistant record in bd", e)
        # logging.warning("Failed to update assistant llm in bd", e)


@db_session
def get_db_assistant(assistant_id) -> Assistant:
    assistant = Assistant.get(assistant_id=assistant_id)

    if assistant is None:
        raise ValueError(f"Assistant with id {assistant_id} not found.")

    return assistant


@db_session
def delete_db_assistant(assistant_id) -> None:
    assistant = Assistant.get(assistant_id=assistant_id)

    if assistant is not None:
        assistant.delete()
    else:
        raise ValueError(f"Assistant with id {assistant_id} not found.")


# ---------------------------- LLM --------------------------------
# @db_session
# def create_db_llm(name) -> None:
#     # llm = LLM.get(name=name)
#     #
#     # if llm is None:
#     #     raise ValueError(f"LLM {name} not found.")
#     try:
#         LLM(name=name)
#     except:
#         raise ValueError(f"Failed to create llm")
#
#     db.commit()


# @db_session
# def get_db_llm(name) -> LLM:
#     llm = LLM.get(name=name)
#
#     if llm is None:
#         raise ValueError(f"LLM {name} not found.")
#
#     return llm


# возвращает список id llm моделей, например: ['gpt-4o', 'gpt-4o-mini', 'gemini-1.5-pro', 'gemini-1.5-flash']
def get_all_llms(api_key, BACKEND_URL) -> list:
    try:
        client = OpenAI(
                api_key=api_key,
                base_url=BACKEND_URL
            )
    except Exception as e:
        logging.error("Failed to create OpenAI object", e)
        return ['openai:gpt-4o', 'openai:gpt-4o-mini']

    models = client.models.list()
    llms = [model.id for model in models.data]

    return llms
