from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler

import locale_module
from auth.auth import get_api_key
from billing.billing_module import BillingAPI, init_invoice, get_invoice_info, convert_to_worken_token
import time
from datetime import datetime

from data.locales import Lexicons
from db.methods import get_dialog_language
from logger import logger


def add_balance_module_handlers(dp):
    dp.add_handler(CallbackQueryHandler(pay_by_card_button_click, pattern='pay_by_card_button_click'))
    dp.add_handler(CallbackQueryHandler(other_pay_button_click, pattern='other_pay_button_click'))
    dp.add_handler(CallbackQueryHandler(cost_details_button_click, pattern='cost_details_button_click'))
    dp.add_handler(CallbackQueryHandler(replenishment_history_button_click, pattern='replenishment_history_button_click'))
    dp.add_handler(CallbackQueryHandler(terms_button_click, pattern='terms_button_click'))
    dp.add_handler(CallbackQueryHandler(wait_on_payment, pattern='wait_on_payment'))
    dp.add_handler(CallbackQueryHandler(offer_button_click, pattern='offer_button_click'))


def pay_by_card_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    api_key = get_api_key(chat_id)[1]["api_key"]
    billing = BillingAPI(api_key=api_key)
    offers = billing.get_offers()
    keyboard = []
    reply_text = ''

    for i, offer in enumerate(offers):
        tax_type = locale_module.get_text(offer["type"], get_dialog_language(chat_id), Lexicons)
        price = convert_to_worken_token(offer["value"])
        reply_text += f'\n{i+1}. {str(tax_type)} {price}  руб.'
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f'{i+1}. {tax_type}',
                    callback_data=f'offer_button_clicked:{offer["id"]}')
            ]
        )

    query.answer()
    query.edit_message_text(
        # TODO написать текстовки для сообщения с описанием предложений и стоимостью
        text=f'''Какой тариф Вас интересует?{reply_text}''',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



def offer_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    _, offer_id = query.data.split(":")
    logger.info(f"chat_id={chat_id} offer_id={offer_id}")

    invoice = init_invoice(chat_id, offer_id)
    logger.info(f"invoice initialized with id={invoice['id']}")

    query.answer()
    query.edit_message_text(
        text=f"Ссылка на оплату: [оплатить]({invoice['url']})",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="Проверить оплату",
                callback_data=f'wait_on_payment:{invoice["id"]}',
            )]
        ])
    )


# переименовать wait_on_payment -> check_payment??
def wait_on_payment(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = str(query.message.chat_id)

    _, invoice_id = query.data.split(":")
    logger.info(f"invoice_id={invoice_id}")

    invoice_status = get_invoice_info(chat_id, invoice_id)["status"]
    max_request_cnt = 1    # максимальное количество запросов, после которого мы перестаем ждать оплату
    latency = 2            # задержка в секундах

    # ожидаем оплаты (смены статуса invoice)
    # request_cnt * latency = максимальное время (в cекундах), которое мы ждем оплату
    # TODO установить макс время ожидание оплаты - 600 секунд
    while invoice_status == 'pending' and max_request_cnt > 0:
        logger.info(f" started waiting status={invoice_status}, requests_left={max_request_cnt}")
        # запрашиваем статус оплаты каждые 10 секунд
        time.sleep(latency)
        invoice_status = get_invoice_info(chat_id, invoice_id)["status"]
        max_request_cnt -= 1

    query.answer()
    # если счет оплачен
    if invoice_status == 'paid':
        logger.info(f"OK invoice_id={invoice_id} invoice_status={invoice_status}")
        query.edit_message_text(
            text='Счет оплачен!',
        )
    else:
        logger.info(f"RUNTIME invoice_id={invoice_id} invoice_status={invoice_status}")
        query.edit_message_text(
            text='Оплата не прошла :(',
        )


# в бэклог
def other_pay_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="other_pay")


# в бэклог
def cost_details_button_click(update: Update, context: CallbackContext) -> None:
    # TODO получить детали расходов (бэк), + парсер данных
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    query.edit_message_text(text="cost_details")



def replenishment_history_button_click(update: Update, context: CallbackContext) -> None:
    # TODO получить историю пополнений (бэк), + парсер данных
    query = update.callback_query
    chat_id = str(query.message.chat_id)
    query.answer()

    repl_histiry_text = ''
    api_key = get_api_key(chat_id)[1]["api_key"]

    billing = BillingAPI(api_key)
    invoices = billing.get_invoices()
    offers = billing.get_offers()

    if len(invoices) == 0:
        query.edit_message_text(
            text='История пополнений:\n\n'
                 'У вас пока что не было пополнений'
        )
    else:
        for invoice in invoices:
            for offer in offers:
                if offer["id"] == invoice["offer_id"]:
                    tax_type = locale_module.get_text(f'{offer["type"]}', get_dialog_language(chat_id), Lexicons)
                    tax_sum = offer["value"]
            if invoice["status"] == "paid":
                invoice_created_at = datetime.fromisoformat(invoice["created_at"][:-1])
                invoice_created_at = invoice_created_at.strftime("%d-%m-%Y %H:%M")
                repl_histiry_text += f'{invoice_created_at}  {tax_type} {tax_sum}\n'


        query.edit_message_text(
            text='История пополнений:\n\n'+repl_histiry_text
        )


def terms_button_click(update: Update, context: CallbackContext) -> None:
    # TODO ссылка на пользовательское соглашение
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="terms")

