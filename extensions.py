import requests
import json

from config import currencies, freecurrencyapi

class ConvertionException(Exception):
    pass

class CurrencyError(ConvertionException):
    pass

class APIException(ConvertionException):
    pass

class Converter:
    def check_currency(self, base_currency=None):
        try:
            if base_currency == None:
                currencies[self]
            else:
                if currencies[self] == currencies[base_currency]:
                    raise CurrencyError(f'❗️Нельзя выбирать одинаковую валюту!\n\n Повторите ввод или введите соответствующую команду:\n👉 Возврат в главное меню: /start\n👉 Список всех доступных валют: /currency\n👉 Помощь: /help')
        except KeyError:
            raise CurrencyError(f'❗️Неверно введена валюта!\n\n Повторите ввод или введите соответствующую команду:\n👉 Возврат в главное меню: /start\n👉 Список всех доступных валют: /currency\n👉 Помощь: /help')

    def check_amount(self):
        try:
            float(self)
        except ValueError:
            raise CurrencyError(f'❗️Неверно указано количество валюты!\n\n Повторите ввод или введите соответствующую команду:\n👉 Возврат в главное меню: /start\n👉 Список всех доступных валют: /currency\n👉 Помощь: /help')

    def cut_symbols(self):
        result = self
        for currency, properties in currencies.items():
            result = result.replace(properties["flag"], '')
        result = result.strip().capitalize()
        return result

    @staticmethod
    def get_price(base, quoted, amount):
        try:
            r = requests.get(f"https://api.freecurrencyapi.com/v1/latest?apikey={freecurrencyapi}&currencies={currencies[quoted]['iso_code']}&base_currency={currencies[base]['iso_code']}")
            price = float(json.loads(r.content)['data'][currencies[quoted]['iso_code']]) * float(amount)
        except ValueError:
           raise APIException(f'❌ Отсутствует подключение к серверу!')
        return round(price, 2)