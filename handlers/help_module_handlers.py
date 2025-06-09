from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler


def add_help_module_handlers(dp):
    dp.add_handler(CallbackQueryHandler(support_button_click, pattern='support_button_click'))


def support_button_click(update: Update, context: CallbackContext) -> None:
    # TODO модуль поддержки?
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="support")