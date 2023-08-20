import telebot
from telebot import types
from config import token, currencies, buttons
from extensions import *

bot = telebot.TeleBot(token)

def create_inline_menu(exclude=None):
    menu = []
    for keys, values in buttons.items():
        if exclude != keys:
            menu.append(types.InlineKeyboardButton(values, callback_data=keys))
    markup = types.InlineKeyboardMarkup()
    markup.add(*menu)
    return markup


def hide_inline_menu(message):
    for i in range(9):
        try:
            bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id-i, reply_markup=None)
        except Exception:
            pass

def create_reply_menu(exclude=None):
    buttons = []
    if exclude == None:
        for currency, properties in currencies.items():
            buttons.append(properties['flag'] + ' ' + currency)
    else:
        for currency, properties in currencies.items():
            if exclude != currency:
                buttons.append(properties['flag'] + ' ' + currency)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=3)
    markup.add(*buttons)
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'convert':
        convert(call.message)
    elif call.data == 'currency':
        currency(call.message)
    elif call.data == 'help':
        help(call.message)
    elif call.data == 'start':
        start(call.message)

@bot.message_handler(commands=['currency'])
def currency(message):
    hide_inline_menu(message)
    text = 'Доступные валюты:'
    for currency, properties in currencies.items():
        text = '\n'.join((text, properties['flag'] +  ' ' + currency, ))
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, text, reply_markup=markup)
    text = 'Воспользуйтесь меню или введите соответствующую команду:\n👉 Возврат в главное меню: /start\n👉 Начать конвертацию: /convert\n👉 Помощь: /help'
    markup = create_inline_menu(exclude='currency')
    bot.send_message(message.chat.id, text,  reply_markup=markup)

@bot.message_handler(commands=['help'])
def help(message):
    hide_inline_menu(message)
    text = 'Чтобы начать конвертацию выберите в меню пункт «Конвертация» или введите команду /convert.\n\nЗатем пройдите последовательно по шагам:\n1️⃣ Выберите или введите название валюты из которой хотите конвертировать\n2️⃣ Выберите или введите название валюты в которую хотите конвертировать\n3️⃣ Укажите количесво валюты'
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, text, reply_markup=markup)
    text = 'Воспользуйтесь меню или введите соответствующую команду:\n👉 Возврат в главное меню: /start\n👉 Начать конвертацию: /convert\n👉 Список всех доступных валют: /currency'
    markup = create_inline_menu(exclude='help')
    bot.send_message(message.chat.id, text,  reply_markup=markup)

@bot.message_handler(commands=['convert'])
def convert(message, stop=False):
    hide_inline_menu(message)
    text = 'Выберите в меню или введите валюту из которой хотите конвертировать:'
    markup = create_reply_menu()
    bot.send_message(message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(message, base_handler)

def base_handler(message: telebot.types.Message):
    base = Converter.cut_symbols(message.text)
    if base == '/start':
        start(message)
    elif base == '/currency':
        currency(message)
    elif base == '/help':
        help(message)
    else:
        try:
            Converter.check_currency(base)
        except CurrencyError as e:
            markup = create_reply_menu()
            bot.send_message(message.chat.id, e, reply_markup=markup)
            bot.register_next_step_handler(message, base_handler)
        else:
            markup = create_reply_menu(base)
            text = 'Выберите в меню или введите валюту в которую хотите конвертировать:'
            bot.send_message(message.chat.id, text, reply_markup=markup)
            bot.register_next_step_handler(message, quoted_handler, base)


def quoted_handler(message: telebot.types.Message, base):
    quoted = Converter.cut_symbols(message.text)
    if quoted == '/start':
        start(message)
    elif quoted == '/currency':
        currency(message)
    elif quoted == '/help':
        help(message)
    else:
        try:
            Converter.check_currency(quoted, base)
        except CurrencyError as e:
            markup = create_reply_menu(base)
            bot.send_message(message.chat.id, e, reply_markup=markup)
            bot.register_next_step_handler(message, quoted_handler, base)
        else:
            text = 'Введите количество конвертируемой валюты:'
            markup = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, text, reply_markup=markup)
            bot.register_next_step_handler(message, amount_handler, base, quoted)

def amount_handler(message: telebot.types.Message, base, quoted):
    amount = message.text.strip()
    if amount == '/start':
        start(message)
    elif amount == '/currency':
        currency(message)
    elif amount == '/help':
        help(message)
    else:
        try:
            amount = amount.replace(",",".")
            Converter.check_amount(amount)
        except CurrencyError as e:
            bot.send_message(message.chat.id, e)
            bot.register_next_step_handler(message, amount_handler, base, quoted)
        else:
            try:
                price = Converter.get_price(base, quoted, amount)
            except APIException as e:
                bot.send_message(message.chat.id, e)
                start(message)
            else:
                markup = create_inline_menu(exclude='start')
                text = f"{round(float(amount), 2)} {currencies[base]['ending'][int(str(round(float(amount), 2))[-1])]}, это {price} {currencies[quoted]['ending'][int(str(price)[-1])]}\n\nВоспользуйтесь меню или введите соответствующую команду:\n👉 Начать новую конвертацию: /convert\n👉 Список всех доступных валют: /currency\n👉 Помощь: /help"
                bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(content_types=['text'], )
def start(message: telebot.types.Message):
    hide_inline_menu(message)
    text = 'Добро пожаловать в конвертер валют БРИКС!🇧🇷🇷🇺🇮🇳🇨🇳🇿🇦'
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, text, reply_markup=markup)
    text = 'Воспользуйтесь меню или введите соответствующую команду:\n👉 Начать конвертацию: /convert\n👉 Список всех доступных валют: /currency\n👉 Помощь: /help'
    markup = create_inline_menu(exclude='start')
    bot.send_message(message.chat.id, text, reply_markup=markup)

bot.polling(none_stop=True)