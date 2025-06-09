from pony.orm import *
from db.db_module import db

class Dialog(db.Entity):
    chat_id = Required(str, unique=True)
    confirmed = Required(bool)
    language = Required(str)
    subscription_status = Required(str)
    current_assistant_id = Optional(str)
    current_llm = Required(str)
    assistants = Set("Assistant", reverse='dialog')
    save_context = Required(bool)
    api_key = Required(str)


class Assistant(db.Entity):
    assistant_id = Required(str, unique=True)
    dialog = Required('Dialog', reverse='assistants')
    llm = Required(str)
    thread_id = Required(str)


# class LLM(db.Entity):
#     name = Required(str, unique=True)
#     assistant = Set('Assistant', reverse='llm')
#     dialog = Set('Dialog', reverse='llms')

