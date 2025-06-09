import logging
from typing import List

from telegram import BotCommandScopeChat, BotCommand, Bot, ChatAction
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext, ConversationHandler

import locale_module
from auth.auth import get_api_key
from billing.billing_module import get_current_balance, get_billing_account_info, get_billing_grants_count
from config import *
from data.locales import Lexicons
from db.methods import *
from db.db_module import *
from assistant.assistant_module import get_assistant, create_assistant, get_answer_from_assistant, create_thread, \
    delete_context, get_assistant


def set_menu(commands: List[BotCommand], update: Update) -> None:
    try:
        bot = Bot(BOT_TOKEN)
        bot.delete_my_commands()
    except Exception as e:
        logging.error("Failed delete Bot commands:\n", e)
        return

    try:
        if update:
            query = update.callback_query
            query.answer()
            bot.set_my_commands(
                commands=commands,
                scope=BotCommandScopeChat(
                    chat_id=query.message.chat_id
                )
            )
        else:
            default_commands = [
                ('my_assistants', locale_module.get_text('my_assistants_button', 'en', Lexicons)),
                ('assistant_settings', locale_module.get_text('assistant_settings_button', 'en', Lexicons)),
                ('delete_context', locale_module.get_text('delete_context_button', 'en', Lexicons)),
                ('change_model', locale_module.get_text('change_model_button', 'en', Lexicons)),
                ('billing', locale_module.get_text('billing_button', 'en', Lexicons)),
                # ('memorize_context', locale_module.get_text('memorize_context_button', 'en', Lexicons)),
                ('help', locale_module.get_text('help_button', 'en', Lexicons)),
            ]
            bot.set_my_commands(commands=default_commands)
    except Exception as e:
        logging.error("Failed to set bot commands:\n", e)


def send_request_to_assistant(update: Update, context: CallbackContext) -> None:
    if not is_user_subscribed(update, context):
        # отправляем сообщение, где можно подтвердить подписку
        subscription_confirmed(update, context)
    else:
        chat_id = str(update.message.chat_id)
        message_text = update.message.text

        connect_to_db()

        # check как мы обрабатываем исключение, если диалог не найден?
        try:
            dialog = get_dialog(chat_id)
        except Exception as e:
            # check что мы делаем, когда диалог не найден?
            logging.error("Failed to get dialog in send_request_to_assistant function", e)
            api_key = get_api_key(chat_id)[1]["api_key"]
            thread_id = create_thread(chat_id)
            assistant_id = create_assistant(chat_id=chat_id, name="Default Assistant", instructions="").id
            dialog = create_dialog(chat_id, api_key)
            update_dialog(chat_id=chat_id, current_assistant_id=assistant_id)

        if len(get_dialog_assistants_ids(chat_id)) == 0:
            update.message.reply_text(
                f'У Вас пока нет ассистентов. Вы можете создать первого ассистента в разделе Мои ассистенты'
            )
            logging.info(f"Cant send request to assistant: no assistants in chat chat_id={chat_id}")
            return ConversationHandler.END
        else:
            assistant_id = dialog.current_assistant_id
            logging.info(f"Sent request to assistant assistant_id={assistant_id} chat_id={chat_id}")
            # check пересмотреть этот блок и мб убрать try except
            try:
                # assistant_name = get_assistant(chat_id, assistant_id).name
                status, reply_text = get_answer_from_assistant(chat_id, message_text)

                if status:
                    update.message.reply_text(
                        text=f'{reply_text}',
                        reply_to_message_id=update.message.message_id
                    )
                    logging.info(f"got reply from assistant: {assistant_id} chat_id={chat_id}")
                else:
                    update.message.reply_text(
                        text=f'{reply_text}',
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton(
                                text=locale_module.get_text('pay_by_card_button', get_dialog_language(chat_id), Lexicons),
                                callback_data='pay_by_card_button_click'
                            )],
                        ]),
                        reply_to_message_id=update.message.message_id
                    )
                return ConversationHandler.END
            except Exception as e:
                update.message.reply_text(
                    text=f'Упс.. что-то пошло не так. \nПо техническим причинам ассистенты недоступны\nПриносим свои извинения за доставленные неудобства',
                    reply_to_message_id=update.message.message_id
                )
                logging.error(f"can`t send request to assistant={assistant_id} chat_id={chat_id}", e)
                return ConversationHandler.END


def change_language(chat_id, new_lang) -> None:
    connect_to_db()
    try:
        get_dialog(chat_id)
    except:
        api_key = get_api_key(chat_id)[1]["api_key"]
        assistant_id = create_assistant(chat_id=chat_id, name="Default Assistant", instructions="").id
        tread_id = create_thread(chat_id)
        create_dialog(chat_id, api_key)
        update_dialog(chat_id=chat_id, current_assistant_id=assistant_id)
        logging.info("Failed to find dialog in module change_language, creating new...")
    try:
        update_dialog(chat_id=chat_id, language=new_lang)
        logging.info(f"changed language chat_id={chat_id}")
    except Exception as e:
        logging.error(f"Failed to change language in chat_id={chat_id}", e)


def set_language(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    connect_to_db()

    languages = {
        'lang_en': 'en',
        'lang_ru': 'ru',
    }

    language = languages.get(query.data, 'en')
    change_language(chat_id, language)

    keyboard = [
        [
            InlineKeyboardButton(
                text=locale_module.get_text('terms_button', language, Lexicons),
                url='https://worken.ai/user-agreement',
            ),
        ],
        [
            InlineKeyboardButton(
                text=locale_module.get_text('confirm_terms_button', language, Lexicons),
                callback_data='termes_confirmed',
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if get_dialog(chat_id).confirmed:
        commands = [
            ('my_assistants', locale_module.get_text('my_assistants_button', language, Lexicons)),
            ('assistant_settings', locale_module.get_text('assistant_settings_button', language, Lexicons)),
            ('delete_context', locale_module.get_text('delete_context_button', language, Lexicons)),
            ('change_model', locale_module.get_text('change_model_button', language, Lexicons)),
            ('billing', locale_module.get_text('billing_button', language, Lexicons)),
            # ('memorize_context', locale_module.get_text('memorize_context_button', language, Lexicons)),
            ('help', locale_module.get_text('help_button', language, Lexicons)),
        ]
        set_menu(
            commands=commands,
            update=update,
        )

    query.answer()
    query.edit_message_text(
        text=locale_module.get_text('terms', get_dialog_language(chat_id), Lexicons),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    # logging.info(f"set language={language} chat_id={chat_id}")


def termes_confirmed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    connect_to_db()

    try:
        language = get_dialog_language(chat_id)
    except:
        language = 'ru'

    if query.data == 'termes_confirmed':
        update_dialog(chat_id, confirmed=True)

        keyboard = [
            [
                InlineKeyboardButton(
                    text=locale_module.get_text('telegram_subscription_button', 'ru', Lexicons),
                    url='https://t.me/worken_ai_channel',
                ),
            ],
            [
                InlineKeyboardButton(
                    text=locale_module.get_text('confirm_telegram_subscription_button', 'ru', Lexicons),
                    callback_data='subscription_confirmed',
                ),
            ]
        ]

        query.answer()
        query.edit_message_text(
            text=locale_module.get_text('telegram_subscription', language, Lexicons),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
        logging.info(f"termes confirmed chat_id={chat_id}")
    else:
        query.answer()
        query.edit_message_text(
            text=locale_module.get_text('terms', language, Lexicons),
            parse_mode=ParseMode.MARKDOWN,
        )


def is_user_subscribed(update: Update, context: CallbackContext) -> bool:
    if update.message:  # если это команда
        user_id = update.message.from_user.id
    elif update.callback_query:  # если это нажатие на кнопку
        query = update.callback_query
        user_id = query.from_user.id

    try:
        chat_member = context.bot.get_chat_member("@worken_ai_channel", user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        return False


# проверка подписки на телеграм канал
def subscription_confirmed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id) if query else str(update.message.chat_id)

    connect_to_db()

    try:
        language = get_dialog_language(chat_id)
    except:
        language = 'ru'

    try:
        # проверяем подписан ли пользователь на тг канал
        if is_user_subscribed(update, context):
            update_dialog(chat_id=chat_id, confirmed=True)

            commands = [
                ('my_assistants', locale_module.get_text('my_assistants_button', language, Lexicons)),
                ('assistant_settings', locale_module.get_text('assistant_settings_button', language, Lexicons)),
                ('delete_context', locale_module.get_text('delete_context_button', language, Lexicons)),
                ('change_model', locale_module.get_text('change_model_button', language, Lexicons)),
                ('billing', locale_module.get_text('billing_button', language, Lexicons)),
                # ('memorize_context', locale_module.get_text('memorize_context_button', language, Lexicons)),
                ('help', locale_module.get_text('help_button', language, Lexicons)),
            ]

            set_menu(
                commands=commands,
                update=update,
            )
            logging.info(f"Subscription confirmed chat_id={chat_id}")
            response_text = locale_module.get_text('hello_message', language, Lexicons)
            if query:
                query.answer()
                query.edit_message_text(text=response_text, parse_mode=ParseMode.MARKDOWN)
            else:
                context.bot.send_message(chat_id=chat_id, text=response_text, parse_mode=ParseMode.MARKDOWN)
        else:
            # если не подписан, то выводим сообщение (всплывающее окно только для callback-запроса)
            alert_text = "Вы не подписаны на канал."
            if query:
                query.answer(text=alert_text, show_alert=True)
            else:
                start_command_handler(update, context)
    except Exception as e:
        logging.error(f"Failed to check subscription in chat_id={chat_id}: {e}")
        error_text = "Не удалось проверить подписку. Пожалуйста, перезапустите бота."
        if query:
            query.edit_message_text(text=error_text)
        else:
            context.bot.send_message(chat_id=chat_id, text=error_text)


def start_command_handler(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.message.chat_id)
    connect_to_db()

    # keyboard = [
    #     [
    #         InlineKeyboardButton(
    #             text=locale_module.get_text('terms_button', 'ru', Lexicons),
    #             url='https://worken.ai/user-agreement',
    #         ),
    #     ],
    #     [
    #         InlineKeyboardButton(
    #             text=locale_module.get_text('confirm_terms_button', 'ru', Lexicons),
    #             callback_data='termes_confirmed',
    #         ),
    #     ]
    # ]
    keyboard = [
        [
            InlineKeyboardButton(
                text=locale_module.get_text('telegram_subscription_button', 'ru', Lexicons),
                url='https://t.me/worken_ai_channel',
            ),
        ],
        [
            InlineKeyboardButton(
                text=locale_module.get_text('confirm_telegram_subscription_button', 'ru', Lexicons),
                callback_data='subscription_confirmed',
            ),
        ]
    ]

    # пробуем найти диалог
    try:
        get_dialog(chat_id)
    except Exception as e:
        # срабатыавет исключение - создаем новый диалог
        # TODO добавить проверку на статус ответа
        api_key = get_api_key(chat_id)[1]["api_key"]
        create_dialog(chat_id, api_key)
        assistant_id = create_assistant(chat_id=chat_id, name="Default Assistant", instructions="").id
        update_dialog(chat_id=chat_id, current_assistant_id=assistant_id, language='ru')

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    update.message.reply_text(
        text=locale_module.get_text('telegram_subscription', 'ru', Lexicons),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )
    logging.info(f"start command clicked chat_id={chat_id}, check_subscription")



def delete_context_command_handler(update: Update, context: CallbackContext) -> None:
    if not is_user_subscribed(update, context):
        # отправляем сообщение, где можно подтвердить подписку
        subscription_confirmed(update, context)
    else:
        chat_id = str(update.message.chat_id)
        api_key = get_api_key(chat_id)[1]["api_key"]

        connect_to_db()
        dialog = get_dialog(chat_id)
        assistant_id = dialog.current_assistant_id

        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)

        try:
            delete_context(api_key, assistant_id)
            send_info_message(update, context, additional_text=locale_module.get_text('delete_context_text', get_dialog_language(chat_id), Lexicons))
            # update.message.reply_text(locale_module.get_text('delete_context_text', get_dialog_language(chat_id), Lexicons))
            logging.info(f"Context deleted chat_id={chat_id}")
        except Exception as e:
            update.message.reply_text(locale_module.get_text('failed_delete_context_text', get_dialog_language(chat_id), Lexicons))
            logging.warning(f"Failed to delete context chat_id={chat_id}", e)

        return ConversationHandler.END


def handle_callback_button_click(update: Update, text_message_key, reply_markup=None) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    connect_to_db()

    query.answer()
    query.edit_message_text(
        text=locale_module.get_text(text_message_key, get_dialog_language(chat_id), Lexicons),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END


def handle_command_click(update: Update, text_message_key, reply_markup=None) -> None:
    chat_id = str(update.message.chat_id)

    connect_to_db()

    update.message.reply_text(
        text=locale_module.get_text(text_message_key, get_dialog_language(chat_id), Lexicons),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END


def generate_buttons(buttons_data, chat_id):
    connect_to_db()
    buttons = []
    for k in buttons_data:
        buttons.append(
            [InlineKeyboardButton(
                locale_module.get_text(k, get_dialog_language(chat_id), Lexicons),
                callback_data=f'{buttons_data[k]}',
            )]
        )
    return buttons


def billing_command_handler(update: Update, context: CallbackContext) -> None:
    if not is_user_subscribed(update, context):
        # отправляем сообщение, где можно подтвердить подписку
        subscription_confirmed(update, context)
    else:
        chat_id = str(update.message.chat_id)
        buttons_data = {
                'pay_by_card_button': 'pay_by_card_button_click',
                # 'other_pay_button': 'other_pay_button_click',
                # 'cost_details_button': 'cost_details_button_click',
                'replenishment_history_button': 'replenishment_history_button_click',

        }
        buttons = generate_buttons(buttons_data, chat_id)
        # вручную добавляем кнопку terms и back, потому что terms - кнопка с url (+ сохраняем порядок кнопок)
        buttons.append(
            [InlineKeyboardButton(
                locale_module.get_text('terms_button', get_dialog_language(chat_id), Lexicons),
                url='https://worken.ai/user-agreement',
            )]
        )
        buttons.append(
            [InlineKeyboardButton(
                locale_module.get_text('back_button', get_dialog_language(chat_id), Lexicons),
                # callback_data='send_hello_message',
                callback_data='delete_message',
            )]
        )
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        billing_account_info = {}
        current_balance = ''

        try:
            billing_account_info = get_billing_account_info(chat_id)
            current_balance = get_current_balance(chat_id)
        except Exception as e:
            logging.error(f"billing_command_handler ", e)
            # check
            billing_account_info["tax_type"] = "-"
            current_balance = '-'

        if billing_account_info["tax_type"] is None:
            tax_type = "-"
            current_balance = '-'
        else:
            tax_type = locale_module.get_text(billing_account_info["tax_type"], get_dialog_language(chat_id), Lexicons)

        try:
            grant_tokens_count = get_billing_grants_count(chat_id)
        except Exception as e:
            grant_tokens_count = 0
            logging.error(f"Failed to get billing account grants count chat_id={chat_id}", e)

        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        update.message.reply_text(
            # TODO убрать хардкод
            text=
            f'''(Баланс и расходы)\n\nТип: {tax_type}\nКоличество токенов: {current_balance} + {grant_tokens_count} (бонусные токены)''',
            reply_markup=reply_markup,
        )
        return ConversationHandler.END


def memorize_context_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    connect_to_db()
    dialog = get_dialog(chat_id)
    save_context = dialog.save_context

    # btn_text_key = 'memorize_context_true_button' if not save_context else 'memorize_context_false_button'
    btn_text_key = 'memorize_context_demo_button'
    save_context = True if not save_context else False
    # TODO обновить настройки по запоминанию контекста (у ассистента?)
    update_dialog(chat_id, save_context=save_context)

    buttons_data = {
        # btn_text_key: 'memorize_context_button_click',
        # 'back_button': 'send_hello_message',
        'back_button': 'send_info_message',
    }
    buttons = generate_buttons(buttons_data, chat_id)
    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    # handle_callback_button_click(
    #     update=update,
    #     text_message_key='memorize_context_text',
    #     reply_markup=reply_markup,
    # )
    query.answer()
    query.edit_message_text(
        text="🛠️Данный модуль находится в разарботке...🛠️"
    )

    return ConversationHandler.END


def memorize_context_command_handler(update: Update, context: CallbackContext) -> None:
    if not is_user_subscribed(update, context):
        # отправляем сообщение, где можно подтвердить подписку
        subscription_confirmed(update, context)
    else:
        chat_id = str(update.message.chat_id)

        connect_to_db()
        dialog = get_dialog(chat_id)
        save_context = dialog.save_context

        # check Модуль находится в разработке... Поэтому текстовка для кнопки все время одна и та же
        # btn_text_key = 'memorize_context_true_button' if save_context else 'memorize_context_false_button'
        btn_text_key = 'memorize_context_demo_button'

        buttons_data = {
                # btn_text_key: 'memorize_context_button_click',
                # 'back_button': 'send_hello_message',
                'back_button': 'send_info_message',
        }
        buttons = generate_buttons(buttons_data, chat_id)
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        handle_command_click(
            update=update,
            text_message_key='memorize_context_text',
            reply_markup=reply_markup,
        )

        return ConversationHandler.END


def help_command_handler(update: Update, context: CallbackContext) -> None:
    if not is_user_subscribed(update, context):
        # отправляем сообщение, где можно подтвердить подписку
        subscription_confirmed(update, context)
    else:
        connect_to_db()
        chat_id = str(update.message.chat_id)

        buttons = [
            [InlineKeyboardButton(
                text=locale_module.get_text('suppport_button', get_dialog_language(chat_id), Lexicons),
                url='t.me/workenai_support_bot'
            )],
            [InlineKeyboardButton(
                text=locale_module.get_text('back_button', get_dialog_language(chat_id), Lexicons),
                # callback_data='send_hello_message'
                callback_data='delete_message'
            )]
        ]

        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        handle_command_click(
            update=update,
            text_message_key='help_module_text',
            reply_markup=reply_markup,
        )

        return ConversationHandler.END


# def change_menu(update: Update, context: CallbackContext) -> None:
#     commands = [
#         ('different_menu', "Другое меню"),
#         ('different_menu', "Другое меню"),
#     ]
#     _set_menu(commands, update)


def delete_message(update: Update, context: CallbackContext) -> int:
    if update.message:  # если это команда
        chat_id = str(update.message.chat_id)
        context.bot.delete_message(chat_id, message_id=update.message.message_id)
        return ConversationHandler.END
    elif update.callback_query:  # если это нажатие на кнопку
        query = update.callback_query
        query.answer()
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        return ConversationHandler.END


def send_info_message(update: Update, context: CallbackContext, additional_text: str=None) -> int:
    if update.message:  # если это команда
        chat_id = str(update.message.chat_id)
        dialog = get_dialog(chat_id)
        curr_assistant_id = dialog.current_assistant_id
        assistant = get_assistant(chat_id, curr_assistant_id)

        curr_llm = dialog.current_llm


        instructions = "-" if assistant.instructions is None else assistant.instructions
        # обрезаем инструкции, если их длина больше 100 символов
        instructions = instructions[:80]+"..." if len(instructions) > 100 else instructions
        description = "-" if assistant.description is None else assistant.description
        temperature = "-" if assistant.temperature is None else assistant.temperature
        top_p = "-" if assistant.top_p is None else assistant.top_p

        message_text = f'\nТекущий ассистент: {assistant.name}\nМодель: {curr_llm.split(":")[1]}\nСтоимость генерации: --\n\nИнструкции: {instructions}\nОписание: {description}\nТемпература ответов: {temperature}\nТор Р: {top_p}'

        if additional_text is not None:
            message_text = additional_text + '\n' + message_text

        update.message.reply_text(
            text=message_text,
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    elif update.callback_query:  # если это нажатие на кнопку
        query = update.callback_query
        chat_id = str(query.message.chat_id)

        dialog = get_dialog(chat_id)
        curr_assistant_id = dialog.current_assistant_id
        assistant = get_assistant(chat_id, curr_assistant_id)
        curr_llm = dialog.current_llm

        instructions = "-" if assistant.instructions is None else assistant.instructions
        # обрезаем инструкции, если их длина больше 100 символов
        instructions = instructions[:80] + "..." if len(instructions) > 100 else instructions
        description = "-" if assistant.description is None else assistant.description
        temperature = "-" if assistant.temperature is None else assistant.temperature
        top_p = "-" if assistant.top_p is None else assistant.top_p

        message_text = f'\nТекущий ассистент: {assistant.name}\nМодель: {curr_llm.split(":")[1]}\nСтоимость генерации: --\n\nИнструкции: {instructions}\nОписание: {description}\nТемпература ответов: {temperature}\nТор Р: {top_p}'

        if additional_text is not None:
            message_text = additional_text + '\n' + message_text

        query.answer()
        query.edit_message_text(
            text=message_text,
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END


def send_hello_message(update: Update, context: CallbackContext) -> int:
    handle_callback_button_click(
        update=update,
        text_message_key='hello_message',
    )
    return ConversationHandler.END

# Проверяет, соответсвует ли текущая подписка ожидаемому значению target_sub
# Возвращает true/false
def check_subscription(chat_id: str, target_sub):
    try:
        connect_to_db()
        sub_status = get_dialog_subscription(chat_id)
    except Exception as e:
        logging.error(f"Failed to get subscription status in dialog with id: {chat_id} ", e)
        return None

    return sub_status == target_sub


# проверяет, есть ли у пользователя на счету платные токены
def is_enough_tokens(chat_id: str) -> bool:
    try:
        connect_to_db()
        account_info = get_billing_account_info(chat_id)
        token_amount_str = account_info['balance']

        if token_amount_str == '0':
            return False
        return True
    except Exception as e:
        logging.error(f"Failed to check tokens amount chat_id={chat_id} ", e)
        return False
