from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CallbackContext, ConversationHandler

import locale_module
from data.locales import Lexicons
from main_handlers import handle_callback_button_click, handle_command_click, send_hello_message, send_info_message, \
    delete_message, is_user_subscribed, subscription_confirmed
# from storage_module import *
from db.methods import *
from assistant.assistant_module import update_assistant_llm_model, get_assistant
from auth.auth import get_api_key
from config import OPENAI_API_BASE_URL


def add_llm_module_handlers(dp) -> None:
    dp.add_handler(CallbackQueryHandler(return_to_models, pattern='return_to_models'))
    dp.add_handler(CallbackQueryHandler(llm_button_clicked, pattern='llm_button_clicked'))



def change_model_command_handler(update: Update, context: CallbackContext) -> None:
    if not is_user_subscribed(update, context):
        # отправляем сообщение, где можно подтвердить подписку
        subscription_confirmed(update, context)
    else:
        chat_id = str(update.message.chat_id)
        reply_markup = generate_llm_reply_markup(chat_id)

        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        handle_command_click(
            update=update,
            text_message_key='change_model_module_text',
            reply_markup=reply_markup
        )

        return ConversationHandler.END


def llm_button_clicked(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    function_name, llm = query.data.split(";")
    connect_to_db()
    dialog = get_dialog(chat_id)
    current_llm = dialog.current_llm
    assistant_id = dialog.current_assistant_id

    query.answer()
    if current_llm == llm:
        # send_hello_message(update, context)
        # send_info_message(update, context)
        delete_message(update, context)
    else:
        update_assistant_llm_model(chat_id=chat_id, assistant_id=assistant_id, llm_model=llm)
        update_dialog(chat_id, current_llm=llm)
        update_db_assistant(assistant_id, llm=llm)
        # return_to_models(update, context)
        send_info_message(update, context, additional_text='Модель изменена!')


def generate_llm_reply_markup(chat_id) -> InlineKeyboardMarkup:
    connect_to_db()
    dialog = get_dialog(chat_id)
    api_key = get_api_key(chat_id)[1]["api_key"]
    llm_list = get_all_llms(api_key, OPENAI_API_BASE_URL)

    btn_llm_back = InlineKeyboardButton(
        locale_module.get_text('back_button', get_dialog_language(chat_id), Lexicons),
        # callback_data='send_hello_message',
        callback_data='delete_message',
    )

    if len(llm_list) != 0:
        markup_lending = []

        k = len(llm_list)

        if len(llm_list) % 2 != 0:
            k = len(llm_list) - 1
            markup_lending.append([generate_llm_button(llm_list[k], dialog)])

        for i in range(0, k, 2):
            btn1 = generate_llm_button(llm_list[i], dialog)
            btn2 = generate_llm_button(llm_list[i+1], dialog)
            markup_lending.append([btn1, btn2])

        markup_lending.append([btn_llm_back])

        return InlineKeyboardMarkup(markup_lending)

    return InlineKeyboardMarkup([
        [btn_llm_back],
    ])


def generate_llm_button(llm, dialog) -> InlineKeyboardButton:
    assistant = get_assistant(dialog.chat_id, dialog.current_assistant_id)

    if assistant.model == llm:
        llm_button_text = f'{llm.split(":")[1]} ✅'
    else:
        llm_button_text = f'{llm.split(":")[1]}'

    button = InlineKeyboardButton(
        llm_button_text,
        callback_data=f'llm_button_clicked;{llm}',
    )

    return button



def return_to_models(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    reply_markup = generate_llm_reply_markup(chat_id)

    handle_callback_button_click(
        update=update,
        text_message_key='change_model_module_text',
        reply_markup=reply_markup
    )
