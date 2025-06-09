import logging  # GET `/billing/offers` – список предложений
# GET `/billing/invoices/:id` – счет по id
# GET `/billing/invoices` – список счетов на оплату
# - GET `/billing/account` – биллинг аккаунт
# - GET `/billing/balance` – кредиты
# - POST `/billing/invoices` – создать счет на оплату, там будет `url` для редиректа пользователя
# принимает offer_id
#

import requests
from config import BACKEND_URL
from auth.auth import get_api_key
from datetime import datetime
from decimal import *


class BillingAPI:
    def __init__(self, api_key: str):
        self.base_url = BACKEND_URL
        self.api_key = api_key

    def _get_headers(self):
        headers = {
            'Accept': 'application/json',
        }
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"
        return headers

    def get_offers(self):
        response = requests.get(
            url=f"{self.base_url}/billing/offers",
            headers=self._get_headers()
        )
        return response.json() if response.ok else response.raise_for_status()

    def get_invoice(self, invoice_id):
        response = requests.get(
            url=f"{self.base_url}/billing/invoices/{invoice_id}",
            headers=self._get_headers()
        )
        return response.json() if response.ok else response.raise_for_status()

    def get_invoices(self):
        response = requests.get(
            url=f"{self.base_url}/billing/invoices",
            headers=self._get_headers()
        )
        return response.json() if response.ok else response.raise_for_status()

    def get_account(self):
        response = requests.get(
            url=f"{self.base_url}/billing/account",
            headers=self._get_headers()
        )
        return response.json() if response.ok else response.raise_for_status()

    def get_balance(self):
        response = requests.get(
            url=f"{self.base_url}/billing/balance",
            headers=self._get_headers()
        )
        return response.json() if response.ok else response.raise_for_status()

    def create_invoice(self, offer_id: str):
        data = {'offer_id': offer_id}
        response = requests.post(
            url=f"{self.base_url}/billing/invoices",
            json=data,
            headers=self._get_headers()
        )
        return response.json() if response.ok else response.raise_for_status()

    # test только для тестового режима
    def approve_test_invoice(self, invoice_id: str) -> None:
        data = {'InvId': invoice_id}
        response = requests.post(
            url=f"http://localhost:3000/billing/robokassa/success",
            json=data,
            headers=self._get_headers()
        )


def init_invoice(chat_id: str, offer_id: str):
    api_key = get_api_key(chat_id)[1]["api_key"]

    billing = BillingAPI(api_key)
    invoices = billing.get_invoices()

    for invoice in invoices:
        if invoice["offer_id"] == offer_id and invoice["status"] == 'pending':
            return invoice

    invoice = billing.create_invoice(offer_id)

    # test только в тестовом режиме
    # billing.approve_test_invoice(invoice["id"])

    return invoice


def get_invoice_info(chat_id: str, invoice_id: str):
    api_key = get_api_key(chat_id)[1]["api_key"]

    billing = BillingAPI(api_key)
    invoice = billing.get_invoice(invoice_id)

    return invoice


def get_current_balance(chat_id: str):
    api_key = get_api_key(chat_id)[1]["api_key"]
    billing = BillingAPI(api_key)

    current_balance = billing.get_balance()['balance']

    return current_balance


def get_billing_account_info(chat_id: str) -> list:
    api_key = get_api_key(chat_id)[1]["api_key"]
    billing = BillingAPI(api_key)

    account_info = billing.get_account()

    return account_info


def convert_to_worken_token(value: str) -> Decimal:
    value = Decimal(value)
    # Проводим вычисление
    result = value / 1_000_000_000  # 1 миллиард = 1 w
    # Форматируем результат с точностью два знака после запятой
    return result.quantize(Decimal("1.00"))


def get_billing_grants_count(chat_id: str) -> int:
    api_key = get_api_key(chat_id)[1]["api_key"]
    billing = BillingAPI(api_key)
    grand_token_cnt = 0.00

    try:
        account_info = billing.get_account()
    except Exception as e:
        raise e

    grants_list = account_info["grants"]

    for grant in grants_list:
        if grant['expires_at'] is None:
            # check! convert
            tokens_cnt = float(convert_to_worken_token(grant['balance']))
            grand_token_cnt += tokens_cnt
            continue

        time_stamp = datetime.now()
        grant_expires_at = datetime.fromisoformat(grant["expires_at"][:-1])

        # проверяем не истек ли срок действия токенов
        if grant_expires_at > time_stamp:
            grand_token_cnt += float(convert_to_worken_token(grant['balance']))

    return grand_token_cnt
