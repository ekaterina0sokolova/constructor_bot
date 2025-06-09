import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters, ConversationHandler
from telegram import Bot

import locale_module
from main_handlers import *
from handlers.assistant_module_handlers import *
from handlers.llm_module_handlers import *
from handlers.billing_module_handlers import *
from handlers.help_module_handlers import *
from config import *


def add_command_handlers(dp) -> None:
    fallbacks_list = [
            CommandHandler('cancel_creating_assistant', cancel_creating_assistant),
            CommandHandler("delete_context", delete_context_command_handler),
            CommandHandler("my_assistants", my_assistants_command_handler),
            CommandHandler("assistant_settings", assistant_settings_command_handler),
            CommandHandler("change_model", change_model_command_handler),
            CommandHandler("billing", billing_command_handler),
            CommandHandler("memorize_context", memorize_context_command_handler),
            CommandHandler("help", help_command_handler),
            # CallbackQueryHandler("return_to_my_assistants", pattern=return_to_my_assistants),
            # CallbackQueryHandler("send_hello_message", pattern=send_hello_message),
            CallbackQueryHandler("send_info_message", pattern=send_info_message),
    ]

    # Main menu handlers
    dp.add_handler(CommandHandler("start", start_command_handler))
    dp.add_handler(CommandHandler("delete_context", delete_context_command_handler))
    dp.add_handler(CommandHandler("my_assistants", my_assistants_command_handler))
    dp.add_handler(CommandHandler("assistant_settings", assistant_settings_command_handler))
    dp.add_handler(CommandHandler("change_model", change_model_command_handler))
    dp.add_handler(CommandHandler("billing", billing_command_handler))
    dp.add_handler(CommandHandler("memorize_context", memorize_context_command_handler))
    dp.add_handler(CommandHandler("help", help_command_handler))

    # dp.add_handler(CommandHandler("change_menu", change_menu))
    dp.add_handler(CallbackQueryHandler(set_language, pattern=r'^lang_.*$'))
    dp.add_handler(CallbackQueryHandler(termes_confirmed, pattern='termes_confirmed'))

    # dp.add_handler(CallbackQueryHandler(send_hello_message, pattern='send_hello_message'))
    dp.add_handler(CallbackQueryHandler(send_info_message, pattern='send_info_message'))
    dp.add_handler(CallbackQueryHandler(delete_message, pattern='delete_message'))
    dp.add_handler(CallbackQueryHandler(subscription_confirmed, pattern='subscription_confirmed'))

    new_assistant_conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_assistant_button_clicked, pattern='new_assistant_button_clicked')],
        states={
            ASSISTANT_NAME: [MessageHandler(filters.Filters.text & ~filters.Filters.command, add_assistant_name)],
            ASSISTANT_INSTRUCTIONS: [MessageHandler(filters.Filters.text & ~filters.Filters.command, add_assistant_instructions)],
        },
        fallbacks=fallbacks_list,
    )

    # ------------------------- хэндлеры: изменение параметров ассистента ----------------------------
    # name
    change_assistant_name_conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(assistant_set_name_button_clicked, pattern='assistant_set_name_button_clicked')],
        states={
            NEW_ASSISTANT_NAME: [MessageHandler(filters.Filters.text & ~filters.Filters.command, update_assistant_name_handler)],
        },
        fallbacks=fallbacks_list,
    )
    # description
    change_assistant_description_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(assistant_set_description_button_clicked, pattern='assistant_set_description_button_clicked')],
        states={
            NEW_ASSISTANT_DESCRIPTION: [
                MessageHandler(filters.Filters.text & ~filters.Filters.command, update_assistant_description_handler)],
        },
        fallbacks=fallbacks_list,
    )
    # instructions
    change_assistant_instructions_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(assistant_set_instructions_button_clicked, pattern='assistant_set_instructions_button_clicked')],
        states={
            NEW_ASSISTANT_INSTRUCTIONS: [
                MessageHandler(filters.Filters.text & ~filters.Filters.command, update_assistant_instructions_handler)],
        },
        fallbacks=fallbacks_list,
    )

    # temperature
    change_assistant_temperature_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(assistant_set_temperature_button_clicked, pattern='assistant_set_temperature_button_clicked')],
        states={
            NEW_ASSISTANT_TEMPERATURE: [
                MessageHandler(filters.Filters.text & ~filters.Filters.command, update_assistant_temperature_handler)],
        },
        fallbacks=fallbacks_list,
    )
    # top_p
    change_assistant_top_p_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(assistant_set_top_p_button_clicked, pattern='assistant_set_top_p_button_clicked')],
        states={
            NEW_ASSISTANT_TOP_P: [
                MessageHandler(filters.Filters.text & ~filters.Filters.command, update_assistant_top_p_handler)],
        },
        fallbacks=fallbacks_list,
    )
    # vector_store
    add_assistant_vector_store_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(create_storage_button_clicked, pattern='create_storage_button_clicked')],
        states={
            VECTOR_STORE_NAME: [MessageHandler(filters.Filters.text & ~filters.Filters.command, add_vector_store_name_handler)],
            VECTOR_STORE_DATA: [
                MessageHandler(filters.Filters.document, add_vector_store_data_handler), CommandHandler('done', done)],
        },
        fallbacks=[],
    )

    # подтверждение удаления ассистента
    delete_assistant_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(delete_selected_assistant, pattern='delete_selected_assistant')],
        states={
            CONFIRM_ASSISTANT_DELETION: [
                CallbackQueryHandler(confirm_assistant_deletion_button_clicked, pattern='confirm_assistant_deletion_button_clicked'),
                CallbackQueryHandler(cancel_assistant_deletion, pattern='cancel_assistant_deletion')
            ],
        },
        fallbacks=fallbacks_list,
    )
    # tools

    add_assistant_module_handlers(dp)
    add_llm_module_handlers(dp)
    dp.add_handler(CallbackQueryHandler(memorize_context_button_click, pattern='memorize_context_button_click'))
    add_balance_module_handlers(dp)
    add_help_module_handlers(dp)

    dp.add_handler(new_assistant_conversation_handler)
    dp.add_handler(change_assistant_name_conversation_handler)
    dp.add_handler(change_assistant_description_conversation_handler)
    dp.add_handler(change_assistant_instructions_conversation_handler)
    dp.add_handler(change_assistant_temperature_conversation_handler)
    dp.add_handler(change_assistant_top_p_conversation_handler)
    dp.add_handler(delete_assistant_conversation_handler)
    dp.add_handler(add_assistant_vector_store_conversation_handler)

    dp.add_handler(MessageHandler(filters.Filters.text & ~filters.Filters.command, send_request_to_assistant))


def set_up_running(updater) -> None:
    try:
        if WEBHOOK_URL:
            updater.start_webhook(
                listen='0.0.0.0',
                port=int(WEBHOOK_PORT),
                webhook_url=WEBHOOK_URL,
            )
        else:
            updater.start_polling()
    except Exception as e:
        logging.error("Starting bot error: \n", e)


def main():
    updater = Updater(BOT_TOKEN)

    # updater.bot.setMyCommands(COMMANDS)

    dp = updater.dispatcher
    add_command_handlers(dp)
    set_up_running(updater)
    # run()

    updater.idle()


if __name__ == '__main__':
    main()
    