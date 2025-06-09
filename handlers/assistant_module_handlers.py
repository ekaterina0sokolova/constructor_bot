import logging
import os
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackQueryHandler, CallbackContext, ConversationHandler, CommandHandler

import locale_module
from data.locales import Lexicons
from config import ASSISTANT_NAME, ASSISTANT_INSTRUCTIONS, MAX_ASSISTANT_CNT, CONFIRM_ASSISTANT_DELETION, \
    VECTOR_STORE_DONE
from db.db_module import connect_to_db
from main_handlers import delete_message, send_info_message, handle_command_click, handle_callback_button_click, \
    generate_buttons, check_subscription, is_user_subscribed, subscription_confirmed, is_enough_tokens
# from storage_module import *
from db.methods import *
from assistant.assistant_module import *
from config import NEW_ASSISTANT_NAME, NEW_ASSISTANT_DESCRIPTION, NEW_ASSISTANT_INSTRUCTIONS, NEW_ASSISTANT_TEMPERATURE, NEW_ASSISTANT_TOOLS, NEW_ASSISTANT_TOP_P, VECTOR_STORE_NAME, VECTOR_STORE_DATA



def add_assistant_module_handlers(dp) -> None:
    dp.add_handler(CallbackQueryHandler(return_to_my_assistants, pattern='return_to_my_assistants'))
    dp.add_handler(CallbackQueryHandler(back_button_clicked, pattern='back_button_clicked'))
    dp.add_handler(CallbackQueryHandler(assistant_button_clicked, pattern='assistant_button_clicked'))

    dp.add_handler(CallbackQueryHandler(assistant_set_knowledge_base_button_clicked, pattern='assistant_set_knowledge_base_button_clicked'))
    dp.add_handler(CallbackQueryHandler(assistant_set_tools_button_clicked, pattern='assistant_set_tools_button_clicked'))
    dp.add_handler(CallbackQueryHandler(assistant_instructions_button_clicked, pattern='assistant_instructions_button_clicked'))
    dp.add_handler(CallbackQueryHandler(delete_instructions_button_clicked, pattern='delete_instructions_button_clicked'))
    dp.add_handler(CallbackQueryHandler(pro_settings_button_clicked, pattern='pro_settings_button_clicked'))
    dp.add_handler(CallbackQueryHandler(back_to_settings_button_clicked, pattern='back_to_settings_button_clicked'))
    # dp.add_handler(CallbackQueryHandler(delete_selected_assistant, pattern='delete_selected_assistant'))
    # dp.add_handler(CallbackQueryHandler(cancel_assistant_deletion, pattern='cancel_assistant_deletion'))
    dp.add_handler(CallbackQueryHandler(storage_button_clicked, pattern='storage_button_clicked'))
    # dp.add_handler(CallbackQueryHandler(save_user_choice_button_clicked, pattern='save_user_choice_button_clicked'))
    dp.add_handler(CallbackQueryHandler(assistant_return_to_knowledge_base_list, pattern='assistant_return_to_knowledge_base_list'))
    dp.add_handler(CommandHandler("done", done))


def generate_assistants_reply_markup(chat_id) -> InlineKeyboardMarkup:
    connect_to_db()
    dialog = get_dialog(chat_id)
    assistant_list = get_dialog_assistants_ids(chat_id)

    btn_create_assistant = InlineKeyboardButton(
        locale_module.get_text('create_assistant_button', get_dialog_language(chat_id), Lexicons),
        callback_data='new_assistant_button_clicked',
    )

    if len(assistant_list) != 0:
        markup_lending = []

        k = len(assistant_list)

        if len(assistant_list) % 2 != 0:
            k = len(assistant_list) - 1
            markup_lending.append([generate_assistant_button(assistant_list[k], dialog)])

        for i in range(0, k, 2):
            btn1 = generate_assistant_button(assistant_list[i], dialog)
            btn2 = generate_assistant_button(assistant_list[i+1], dialog)
            markup_lending.append([btn1, btn2])

        markup_lending.append([btn_create_assistant])

        return InlineKeyboardMarkup(markup_lending)

    return InlineKeyboardMarkup([
        [btn_create_assistant],
    ])



def my_assistants_command_handler(update: Update, context: CallbackContext) -> None:
    if not is_user_subscribed(update, context):
        # отправляем сообщение, где можно подтвердить подписку
        subscription_confirmed(update, context)
    else:
        chat_id = str(update.message.chat_id)
        reply_markup = generate_assistants_reply_markup(chat_id)

        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        handle_command_click(
            update=update,
            text_message_key='my_assistants_text',
            reply_markup=reply_markup
        )
        # return ConversationHandler.END



def assistant_button_clicked(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    function_name, assistant_id = query.data.split(":")
    connect_to_db()
    dialog = get_dialog(chat_id)
    current_assistant_id = dialog.current_assistant_id

    query.answer()
    if current_assistant_id == assistant_id:
        query.message.delete()
        # send_info_message(update, context)
        # send_hello_message(update, context)
    else:
        update_dialog(chat_id, current_assistant_id=assistant_id)
        # return_to_my_assistants(update, context)
        send_info_message(update, context, additional_text='Вы сменили активного ассистента.')


def back_button_clicked(update: Update, context: CallbackContext) -> None:
    send_info_message(update, context)


def generate_assistant_button(assistant_id, dialog) -> InlineKeyboardButton:
    connect_to_db()
    assistant_name = get_assistant(dialog.chat_id, assistant_id).name
    if dialog.current_assistant_id == assistant_id:
        assistant_button_text = f'✅ {assistant_name}'
    else:
        assistant_button_text = f'{assistant_name}'

    button = InlineKeyboardButton(
        assistant_button_text,
        callback_data=f'assistant_button_clicked:{assistant_id}',
    )

    return button


def return_to_my_assistants(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    reply_markup = generate_assistants_reply_markup(chat_id)

    handle_callback_button_click(
        update=update,
        text_message_key='my_assistants_text',
        reply_markup=reply_markup
    )
    return ConversationHandler.END


# функция добавления имени при создании нового ассистента
# после ввода пользователем имени ассистента переходит на следующий этап - ввод описания
def add_assistant_name(update: Update, context: CallbackContext) -> int:
    chat_id = str(update.message.chat_id)
    assistant_name = update.message.text

    connect_to_db()

    if is_correct_assistant_name(assistant_name):
        context.user_data['title'] = update.message.text

        update.message.reply_text(
            locale_module.get_text(
                'enter_assistant_instructions_text',
                get_dialog_language(chat_id),
                Lexicons
            )
        )
        return ASSISTANT_INSTRUCTIONS
    else:
        update.message.reply_text(
            locale_module.get_text(
                'assistant_name_length_err_text',
                get_dialog_language(chat_id),
                Lexicons
            ),
        )
        return ASSISTANT_NAME


# ----------------------------- проверки параметров ассистента ------------------------
def is_correct_assistant_name(name) -> bool:
    min_length = 1
    max_length = 20

    return min_length <= len(name) <= max_length


def is_correct_assistant_instructions(instructions) -> bool:
    min_length = 10
    max_length = 1000

    return min_length <= len(instructions) <= max_length


def is_correct_assistant_description(description) -> bool:
    min_length = 10
    max_length = 1000

    return min_length <= len(description) <= max_length


# функция ввода описания ассистента при его создании (второй этап созания ассистента)
def add_assistant_instructions(update: Update, context: CallbackContext) -> int:
    chat_id = str(update.message.chat_id)
    title = context.user_data['title']
    instructions_text = update.message.text

    if is_correct_assistant_instructions(instructions_text):
        connect_to_db()
        assistant = create_assistant(chat_id=chat_id, name=title, instructions=instructions_text)
        update_dialog(chat_id, current_assistant_id=assistant.id)

        # send_info_message
        send_info_message(update, context, additional_text=locale_module.get_text('assistant_created', get_dialog_language(chat_id), Lexicons))
        # handle_command_click(
        #     update=update,
        #     text_message_key='assistant_created',
        # )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            locale_module.get_text(
                'assistant_instructions_length_err_text',
                get_dialog_language(chat_id),
                Lexicons
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        return ASSISTANT_INSTRUCTIONS


def cancel_creating_assistant(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        locale_module.get_text(
            'create_assistant_canceled_text',
            get_dialog_language(str(update.message.chat_id)),
            Lexicons,
        )
    )
    return ConversationHandler.END


# проверяет можем ли мы создать еще одного ассистента (если кол-во ассистентов < максимально допустимого, то можем)
def is_correct_assistant_count(chat_id: str) -> bool:
    assistant_list = get_dialog_assistants_ids(chat_id)

    return len(assistant_list) < MAX_ASSISTANT_CNT


def delete_selected_assistant(update: Update, context: CallbackContext = None) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    dialog = get_dialog(chat_id)
    assistant_id = dialog.current_assistant_id
    assistant = get_assistant(chat_id, assistant_id)
    assistant_name = assistant.name

    query.answer()
    query.edit_message_text(
        # TODO убрать хардкод
        text=f'Подтвердите удаление ассистента: {assistant_name}\n\n *Это действие нельзя будет отменить*',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=locale_module.get_text('confirm_assistant_deletion_btn', get_dialog_language(chat_id), Lexicons),
                callback_data='confirm_assistant_deletion_button_clicked'
            )],
            [InlineKeyboardButton(
                text=locale_module.get_text('back_button', get_dialog_language(chat_id), Lexicons),
                callback_data='cancel_assistant_deletion'
            )]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

    return CONFIRM_ASSISTANT_DELETION


def confirm_assistant_deletion_button_clicked(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    dialog = get_dialog(chat_id)
    assistant_id = dialog.current_assistant_id
    assistant_list = get_dialog_assistants_ids(chat_id)

    # check проверяем остались ли еще ассистенты
    if len(assistant_list) == 1:
        # не даем удалить последнего ассистента
        query.edit_message_text(
            # TODO убрать хардкод
            text=f'Похоже, что у вас остался один ассистент. Для того, чтобы его удалить, сначала создайте нового в разделе "Мои ассистенты"'
        )
        return ConversationHandler.END

    # check рефактор проверки "не совпадает ли установленный new_current_assistant_id удаляемому"
    if assistant_list[0] != assistant_id:
        new_current_assistant_id = assistant_list[0]
    else:
        new_current_assistant_id = assistant_list[1]

    update_dialog(chat_id, current_assistant_id=new_current_assistant_id)

    query.answer()
    try:
        delete_assistant(chat_id, assistant_id)
        # TODO убрать хардкод
        send_info_message(update, context, additional_text="Ассистент удален.")
        return ConversationHandler.END
    except Exception as e:
        logging.warning(f"Failed to delete assistant chat_id={chat_id} assistant_id={assistant_id} error_code=123", e)
        # TODO убрать хардкод
        send_info_message(update, context, additional_text="Упс.. что-то пошло не так - не удалось удалить ассистента. \nЕсли ошибка повторится, пожалуйста, сообщите в поддержку код ошибки: 123")
        return ConversationHandler.END


def cancel_assistant_deletion(update: Update, context: CallbackContext):
    back_to_settings_button_clicked(update, context)
    return ConversationHandler.END


def new_assistant_button_clicked(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    # проверка на количество ассистентов
    if is_correct_assistant_count(chat_id):
        handle_callback_button_click(
            update=update,
            text_message_key='new_assistant_form_text',
        )
        return ASSISTANT_NAME
    else:
        reply_markup = generate_assistants_reply_markup(chat_id)

        # # заменяем кнопку "Создать ассистента" на "Удалить выбранного ассистента"
        # reply_markup["inline_keyboard"][0] = [
        #     InlineKeyboardButton(
        #         text=locale_module.get_text("delete_selected_assistant_button", get_dialog_language(chat_id), Lexicons),
        #         callback_data='delete_selected_assistant'
        #     )
        # ]

        handle_callback_button_click(
            update=update,
            text_message_key='reached_max_assistant_cnt_text',
            reply_markup=reply_markup
        )
        return ConversationHandler.END


def assistant_settings_command_handler(update: Update, context: CallbackContext) -> None:
    if not is_user_subscribed(update, context):
        # отправляем сообщение, где можно подтвердить подписку
        subscription_confirmed(update, context)
    else:
        chat_id = str(update.message.chat_id)
        connect_to_db()

        dialog = get_dialog(chat_id)
        assistant_name = get_assistant(chat_id, dialog.current_assistant_id).name

        # check Модуль находится в разработке... Поэтому текстовка для кнопки все время одна и та же
        memorize_context_btn_text_key = 'memorize_context_demo_button'

        buttons_data = {
            'settings_module_name_button': 'assistant_set_name_button_clicked',
            'settings_module_instructions_button': 'assistant_instructions_button_clicked',
            memorize_context_btn_text_key: 'memorize_context_button_click',
            'pro_settings_text': 'pro_settings_button_clicked',
            'delete_selected_assistant_button': 'delete_selected_assistant',
            'back_button': 'delete_message',
        }
        buttons = generate_buttons(buttons_data, chat_id)
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        # получаем текстовку для сообщения и вставляем в неё название текущего ассистента
        message_text = locale_module.get_text('settings_module_text', get_dialog_language(chat_id), Lexicons)
        message_text = message_text.replace("{assistant_name}", f"{assistant_name}")

        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        update.message.reply_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END


def pro_settings_button_clicked(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    connect_to_db()
    dialog = get_dialog(chat_id)
    assistant_name = get_assistant(chat_id, dialog.current_assistant_id).name

    buttons_data = {
        'settings_module_description_button': 'assistant_set_description_button_clicked',
        'settings_module_top_p_button': 'assistant_set_top_p_button_clicked',
        'settings_module_temperature_button': 'assistant_set_temperature_button_clicked',
        'settings_module_knowledge_base_button': 'assistant_set_knowledge_base_button_clicked',
        'settings_module_tools_button': 'assistant_set_tools_button_clicked',
        'back_button': 'back_to_settings_button_clicked',
    }
    buttons = generate_buttons(buttons_data, chat_id)
    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    # получаем текстовку для сообщения и вставляем в неё название текущего ассистента
    message_text = locale_module.get_text('pro_settings_module_text', get_dialog_language(chat_id), Lexicons)
    message_text = message_text.replace("{assistant_name}", f"{assistant_name}")

    # check delete
    # context.bot.delete_message(chat_id=update.message.chat_id, message_id=query.message.message_id)
    query.answer()
    query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END


# возвращаемся в модуль настроек ассистентов
def back_to_settings_button_clicked(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    connect_to_db()
    dialog = get_dialog(chat_id)
    assistant_name = get_assistant(chat_id, dialog.current_assistant_id).name

    # check Модуль находится в разработке... Поэтому текстовка для кнопки все время одна и та же
    memorize_context_btn_text_key = 'memorize_context_demo_button'

    buttons_data = {
        'settings_module_name_button': 'assistant_set_name_button_clicked',
        'settings_module_instructions_button': 'assistant_instructions_button_clicked',
        memorize_context_btn_text_key: 'memorize_context_button_click',
        'pro_settings_text': 'pro_settings_button_clicked',
        'delete_selected_assistant_button': 'delete_selected_assistant',
        'back_button': 'delete_message',
    }
    buttons = generate_buttons(buttons_data, chat_id)
    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    # получаем текстовку для сообщения и вставляем в неё название текущего ассистента
    message_text = locale_module.get_text('settings_module_text', get_dialog_language(chat_id), Lexicons)
    message_text = message_text.replace("{assistant_name}", f"{assistant_name}")

    # check delete
    # context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    query.answer()
    query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END


# ------------------------------ обработчики нажатия на кнопки меню (вызов команд) ----------------------
def assistant_set_name_button_clicked(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    # sub check
    if not check_subscription(chat_id, "free"):
        query.edit_message_text(text="wrong_subscription")
        return ConversationHandler.END

    query.answer()
    handle_callback_button_click(
        update=update,
        text_message_key='update_assistant_name_text',
    )

    return NEW_ASSISTANT_NAME


def assistant_set_description_button_clicked(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    if not check_subscription(chat_id, "free"):
        query.edit_message_text(text="wrong_subscription")
        return ConversationHandler.END

    handle_callback_button_click(
        update=update,
        text_message_key='description_button_clicked',
    )

    return NEW_ASSISTANT_DESCRIPTION


# функция вызывается при нажатии на кнопку "Инструкции" в модуле Проф настроек
def assistant_instructions_button_clicked(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    current_assistant_id = get_dialog(chat_id).current_assistant_id

    try:
        assistant = get_assistant(chat_id, assistant_id=current_assistant_id)
        current_assistant_instructions = assistant.instructions

        if len(current_assistant_instructions) > 200:
            # обрезаем инструкции для вывода в сообщение только первых 200 символов + добавляем знак троеточия
            current_assistant_instructions = current_assistant_instructions[:200] + "..."
    except Exception as e:
        logging.error(f"Failed to get assistant instructions chat_id={chat_id} assistant_id={current_assistant_id}")
        current_assistant_instructions = "-"

    reply_text = locale_module.get_text('instructions_module_text', get_dialog_language(chat_id), Lexicons)
    reply_text = reply_text.replace('{current_assistant_instructions}', f'"{current_assistant_instructions}"')

    query.answer()
    query.edit_message_text(
        text=reply_text,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(
                    locale_module.get_text('set_instructions_button_text', get_dialog_language(chat_id), Lexicons),
                    callback_data='assistant_set_instructions_button_clicked',
                )],
                [InlineKeyboardButton(
                    locale_module.get_text('delete_instructions_button_text', get_dialog_language(chat_id), Lexicons),
                    callback_data='delete_instructions_button_clicked', # добавить хэндлер
                )],
                [InlineKeyboardButton(
                    locale_module.get_text('back_button', get_dialog_language(chat_id), Lexicons),
                    callback_data="back_to_settings_button_clicked",
                )],
            ]
        ),
        parse_mode=ParseMode.MARKDOWN
    )


# функция вызывается при нажатии на кнопку "Задать инструкции"
def assistant_set_instructions_button_clicked(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    if not check_subscription(chat_id, "free"):
        query.edit_message_text(text="wrong_subscription")
        return ConversationHandler.END

    handle_callback_button_click(
        update=update,
        text_message_key='instructions_button_clicked',
    )

    return NEW_ASSISTANT_INSTRUCTIONS


def delete_instructions_button_clicked(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    dialog = get_dialog(chat_id)
    update_assistant_instructions(chat_id, assistant_id=dialog.current_assistant_id, instructions='')

    send_info_message(
        update,
        context,
        additional_text=locale_module.get_text('instructions_deleted_text', get_dialog_language(chat_id), Lexicons)
    )

def assistant_set_top_p_button_clicked(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    if not check_subscription(chat_id, "free"):
        query.edit_message_text(text="wrong_subscription")
        return ConversationHandler.END

    handle_callback_button_click(
        update=update,
        text_message_key='top_p_button_clicked',
    )

    return NEW_ASSISTANT_TOP_P


def assistant_set_temperature_button_clicked(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    if not check_subscription(chat_id, "free"):
        query.edit_message_text(text="wrong_subscription")
        return ConversationHandler.END

    handle_callback_button_click(
        update=update,
        text_message_key='temperature_button_clicked',
    )

    return NEW_ASSISTANT_TEMPERATURE


# --------------------------------------- storage module -----------------------------------------------------------

def generate_storage_reply_markup(chat_id: str):
    # получаем список векторных хранилищ
    try:
        storage_list = get_all_user_storage_list(chat_id)
    except:
        storage_list = []

    # формируем клавиатуру
    # кнопка "Добавить базу знаний"
    create_storage_button = InlineKeyboardButton(
        text=locale_module.get_text('create_storage_button', get_dialog_language(chat_id), Lexicons),
        callback_data='create_storage_button_clicked'
    )
    # кнопка "Сохранить мой выбор"
    # save_user_choice_button = InlineKeyboardButton(
    #     text=locale_module.get_text('save_user_choice_button', get_dialog_language(chat_id), Lexicons),
    #     callback_data='save_user_choice_button_clicked'
    # )
    # кнопка "Назад/в диалог"
    back_button = InlineKeyboardButton(
        text="Назад",
        callback_data='pro_settings_button_clicked'
    )

    reply_keyboard = [[create_storage_button]]

    if len(storage_list) != 0:
        # получаем словарь хранилищ в формате {id: name}, которые использует текущий ассистент
        assistant_storage_dict = get_assistant_storage_dict(chat_id)

        # генерируем кнопки для векторных хранилищ
        for storage in storage_list:
            if storage.id in assistant_storage_dict:
                button_text = f'✅ {storage.name}'
            else:
                button_text = f'{storage.name}'

            storage_btn = InlineKeyboardButton(
                text=button_text,
                callback_data=f'storage_button_clicked;{storage.id}'
            )
            reply_keyboard.append([storage_btn])

    # reply_keyboard.append([save_user_choice_button])
    reply_keyboard.append([back_button])

    return reply_keyboard


def assistant_set_knowledge_base_button_clicked(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    # проверяем, что у пользователя есть платные токены
    if not is_enough_tokens(chat_id):
        delete_message(update, context)
        query.message.reply_text(text=locale_module.get_text("wrong_tokens_amount", get_dialog_language(chat_id), Lexicons))
    else:
        reply_keyboard = InlineKeyboardMarkup(generate_storage_reply_markup(chat_id))

        query.edit_message_text(
            text="Базы знаний",
            reply_markup=reply_keyboard,
        )


def assistant_return_to_knowledge_base_list(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    # проверяем, что у пользователя есть платные токены
    if not is_enough_tokens(chat_id):
        delete_message(update, context)
        query.message.reply_text(text=locale_module.get_text("wrong_tokens_amount", get_dialog_language(chat_id), Lexicons))
    else:
        reply_keyboard = InlineKeyboardMarkup(generate_storage_reply_markup(chat_id))

        query.edit_message_text(
            text="Базы знаний",
            reply_markup=reply_keyboard,
        )


def storage_button_clicked(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    # получаем список всех векторных хранилищ пользоватлея [VectorStore(),...]
    storage_list = get_all_user_storage_list(chat_id)
    # а также словарь хранилищ, которые использует текущий ассистент {id: name, ...}
    current_assistant_storage_dict = get_assistant_storage_dict(chat_id)

    function_name, storage_id = query.data.split(";")
    selected_storage = next((i for i in storage_list if i.id == storage_id), None)

    is_storage_active = False

    for id, name in current_assistant_storage_dict.items():
        # если пользователь нажал на хранилище, которое использует ассистент
        if selected_storage.id == id:
            is_storage_active = True
            break
        else:
            is_storage_active = False

    if is_storage_active:
        current_assistant_storage_dict.pop(selected_storage.id)
    else:
        current_assistant_storage_dict[selected_storage.id] = selected_storage.name

    id_list = list(current_assistant_storage_dict.keys())
    update_assistant_storage_list(chat_id, id_list)

    reply_keyboard = InlineKeyboardMarkup(generate_storage_reply_markup(chat_id))

    # получаем объект VectorStore() для выбранного пользователем хранилища (по id)
    selected_storage = next((i for i in storage_list if i.id == storage_id), None)

    is_storage_active = False

    for id, name in current_assistant_storage_dict.items():
        if selected_storage.id == id:
            is_storage_active = True
            break
        else:
            is_storage_active = False

    # если пользователь нажал на хранилище, которое использует ассистент
    if is_storage_active:
        # убираем хранилище из словаря хранилищ ассистента {id: name}
        current_assistant_storage_dict.pop(selected_storage.id)
    else:
        # добавляем хранилище в словарь хранилищ ассистента {id: name}
        current_assistant_storage_dict[selected_storage.id] = selected_storage.name

    id_list = list(current_assistant_storage_dict.keys())

    # обновляем список
    update_assistant_storage_list(chat_id, id_list)

    reply_keyboard = InlineKeyboardMarkup(generate_storage_reply_markup(chat_id))

    query.edit_message_text(
        text="Базы знаний",
        reply_markup=reply_keyboard,
    )


# def save_user_choice_button_clicked(update: Update, context: CallbackContext) -> None:
#     query = update.callback_query
#     chat_id = str(query.message.chat_id)
#     query.answer()
#
#     query.edit_message_text(
#         text="🛠️Данный модуль находится в разработке...🛠️\nВы нажали на кнопку Сохранить мой выбор",
#     )


def create_storage_button_clicked(update: Update, context: CallbackContext) -> None:
    print("Create vs button clicked")
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    if chat_id in context.user_data:
        context.user_data[chat_id].clear()

    query.answer()

    query.edit_message_text(
        text="Введите название базы знаний:",
    )

    return VECTOR_STORE_NAME


def add_vector_store_name_handler(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.message.chat_id)
    vector_store_name = update.message.text

    connect_to_db()
    context.user_data.clear()

    # check: переделать проверку??
    if len(vector_store_name) != 0:
        context.user_data['title'] = update.message.text

        update.message.reply_text(
            "Как добавить базу знаний: \n\n1. Отправьте файл до 1МБ, формата .txt \n*Можно прикрепить несколько файлов или отправить несколько текстовых сообщений \n\n2. Если Вы отправили всю необходимую информацию и хотите создать базу, то отправьте команду /done - база знаний будет создана на основе отправленных ранее данных."
        )

        return VECTOR_STORE_DATA
    else:
        update.message.reply_text(
            "Упс, название должно содержать хотя бы 1 символ. \n Попробуйте ввести еще раз."
        )
        return VECTOR_STORE_NAME


def add_vector_store_data_handler(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.message.chat_id)

    if 'files' not in context.user_data:
        context.user_data['files'] = []

    # если отправили файлы
    if update.message.document:
        # Получаем все документы из сообщения
        documents = update.message.document

        # Преобразуем в список, если это один документ
        if not isinstance(documents, list):
            documents = [documents]

        file_paths = []

        # Обработка каждого файла
        for document in documents:
            # проверяем расширение
            if not document.file_name.lower().endswith('.txt'):
                update.message.reply_text(
                    "Файл имеет неверный формат.\nПринимаются только файлы .txt. \nПопробуйте еще раз - перейдите в раздел баз знаний и нажмите Добавить базу знаний"
                    )
                return ConversationHandler.END

            logging.debug(f"{document.file_name} format is OK")

            # проверяем размер файла (max 1MB)
            if document.file_size > 1 * 1024 * 1024:
                update.message.reply_text("Файл слишком большой. Максимальный размер - 1МБ. \nПопробуйте еще раз - перейдите в раздел баз знаний и нажмите Добавить базу знаний")
                return ConversationHandler.END

            logging.debug(f"{document.file_name} size is OK")

            # Получаем информацию о файле
            file = document.get_file()

            # создаем временную директорию
            os.makedirs(f'temp_files/{chat_id}', exist_ok=True)

            # Генерируем уникальное имя файла с использованием chat_id и имени файла
            file_name = f"temp_files/{chat_id}/{chat_id}_{document.file_name}"

            # Скачиваем файл
            file.download(file_name)
            logging.debug(f"{document.file_name} downloaded...")
            file_paths.append(file_name)

        context.user_data['files'].append(update.message.document.file_id)

        update.message.reply_text(
            text=f"Файл {document.file_name} загружен"
        )
        return ConversationHandler.END
    else:
    #     # если пользователь загрузил текст

    #     # задаем уникальное имя для файла
    #     filename = f"{chat_id}" + datetime.now().strftime("_file_%Y-%m-%d_%H-%M-%S.txt")
    #     filepath = os.path.join(f'temp_files/{chat_id}', filename)

    #     # проверяем, что существует директория temp_files
    #     os.makedirs(f'temp_files/{chat_id}', exist_ok=True)

    #     with open(filepath, 'w', encoding='utf-8') as f:
    #         f.write(update.message.text)

        update.message.reply_text(
            text=f"Формат данных не определен! Создание БЗ отменено"
        )
        return ConversationHandler.END

    # После загрузки всех файлов пользователь отправляет команду '/done'
    # context.user_data['next_step'] = 'done'
    # return VECTOR_STORE_DONE


def done(update: Update, context: CallbackContext) -> int:
    chat_id = str(update.message.chat_id)

    if 'files' in context.user_data:
        try:
            title = context.user_data['title']
            # получаем список файлов
            files = os.listdir(f"temp_files/{chat_id}")
        except:
            update.message.reply_text(
                text="Файлы не были загружены"
            )
            return ConversationHandler.END

        file_paths = [f"temp_files/{chat_id}/{file}" for file in files]

        # Создание векторного хранилища
        logging.debug(f"creating Vector storage chat_id={chat_id}...")
        try:
            create_vector_storage(chat_id, title, file_paths)
        except Exception as e:
            update.message.reply_text(
                text="Не удалось создать базу знаний"
            )
            return ConversationHandler.END

        logging.debug(f"Vector storage created")

        # удаление временных файлов
        for path in file_paths:
            os.remove(path)

        logging.debug("Temp files deleted")

        reply_keyboard = InlineKeyboardMarkup(generate_storage_reply_markup(chat_id))
        update.message.reply_text(
            text="Базы знаний",
            reply_markup=reply_keyboard,
        )
        context.user_data.clear()
        return ConversationHandler.END
    else:
        context.user_data.clear()
        update.message.reply_text(
            text="Эта команда недоступна в текущем состоянии.",
        )
        return ConversationHandler.END
# --------------------------------------- -----------------------------------------------------------

def assistant_set_tools_button_clicked(update: Update, context: CallbackContext) -> None:
    # TODO set tools ?
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    if not check_subscription(chat_id, "free"):
        query.edit_message_text(text="wrong_subscription")

    query.edit_message_text(text="🛠️Данный модуль находится в разарботке...🛠️")


# ------------------------------------ обработчики ввода новых параметров ассистента -----------------------------------
def update_assistant_name_handler(update: Update, context: CallbackContext) -> int:
    chat_id = str(update.message.chat_id)
    name = update.message.text

    if is_correct_assistant_name(name):
        connect_to_db()
        dialog = get_dialog(chat_id)
        update_assistant_name(chat_id, assistant_id=dialog.current_assistant_id, name=name)

        reply_text = locale_module.get_text(
                'update_assistant_name_done',
                get_dialog_language(chat_id),
                Lexicons
            )

        reply_text = reply_text.replace("{assistant_name}", f'{name}')

        send_info_message(update, context, additional_text=reply_text)
        return ConversationHandler.END
    else:
        update.message.reply_text(
            locale_module.get_text(
                'assistant_name_length_err_text',
                get_dialog_language(chat_id),
                Lexicons
            ),
        )
        return NEW_ASSISTANT_NAME



def update_assistant_description_handler(update: Update, context: CallbackContext) -> int:
    chat_id = str(update.message.chat_id)
    description = update.message.text

    if is_correct_assistant_description(description):
        connect_to_db()
        dialog = get_dialog(chat_id)
        update_assistant_description(chat_id, assistant_id=dialog.current_assistant_id, description=description)

        send_info_message(
            update,
            context,
            additional_text=locale_module.get_text(
                'update_assistant_description_done',
                get_dialog_language(chat_id),
                Lexicons
            )
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            locale_module.get_text(
                'assistant_description_length_err_text',
                get_dialog_language(chat_id),
                Lexicons
            ),
        )
        return NEW_ASSISTANT_DESCRIPTION



def update_assistant_instructions_handler(update: Update, context: CallbackContext) -> int:
    chat_id = str(update.message.chat_id)
    instructions = update.message.text

    if is_correct_assistant_instructions(instructions):
        connect_to_db()
        dialog = get_dialog(chat_id)
        update_assistant_instructions(chat_id, assistant_id=dialog.current_assistant_id, instructions=instructions)

        send_info_message(
            update,
            context,
            additional_text=locale_module.get_text(
                'update_assistant_instructions_done',
                get_dialog_language(chat_id),
                Lexicons
            ),
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            locale_module.get_text(
                'assistant_instructions_length_err_text',
                get_dialog_language(chat_id),
                Lexicons
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        return NEW_ASSISTANT_INSTRUCTIONS



def update_assistant_temperature_handler(update: Update, context: CallbackContext) -> int:
    chat_id = str(update.message.chat_id)

    try:
        temperature = float(update.message.text)
    except:
        update.message.reply_text(
            locale_module.get_text(
                'assistant_temperature_err_text',
                get_dialog_language(chat_id),
                Lexicons
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        return NEW_ASSISTANT_TEMPERATURE

    max_temperature = 1
    min_temperature = 0

    if min_temperature <= temperature <= max_temperature:
        connect_to_db()
        dialog = get_dialog(chat_id)
        update_assistant_temperature(chat_id, assistant_id=dialog.current_assistant_id, temperature=temperature)

        reply_text = locale_module.get_text('update_assistant_temperature_done', get_dialog_language(chat_id), Lexicons)
        reply_text = reply_text.replace("{temperature}", f"*{temperature}*")

        send_info_message(update, context, additional_text=reply_text)
        return ConversationHandler.END
    else:
        update.message.reply_text(
            locale_module.get_text(
                'assistant_temperature_err_text',
                get_dialog_language(chat_id),
                Lexicons
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        return NEW_ASSISTANT_TEMPERATURE



def update_assistant_top_p_handler(update: Update, context: CallbackContext) -> int:
    chat_id = str(update.message.chat_id)

    try:
        top_p = float(update.message.text)
    except:
        update.message.reply_text(
            locale_module.get_text(
                'assistant_top_p_err_text',
                get_dialog_language(chat_id),
                Lexicons
            ),
        )
        return NEW_ASSISTANT_TOP_P

    max_top_p = 1
    min_top_p = 0

    if min_top_p <= top_p <= max_top_p:
        connect_to_db()
        dialog = get_dialog(chat_id)
        update_assistant_top_p(chat_id, assistant_id=dialog.current_assistant_id, top_p=top_p)

        reply_text = locale_module.get_text('update_assistant_top_p_done', get_dialog_language(chat_id), Lexicons)
        reply_text = reply_text.replace("{top_p}", f"*{top_p}*")

        send_info_message(update, context, additional_text=reply_text)
        return ConversationHandler.END
    else:
        update.message.reply_text(
            locale_module.get_text(
                'assistant_top_p_err_text',
                get_dialog_language(chat_id),
                Lexicons
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        return NEW_ASSISTANT_TOP_P

