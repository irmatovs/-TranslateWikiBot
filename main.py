from configs import *
from telebot import TeleBot
from googletrans import Translator  # Google
# from translate import Translator  # Microsoft
from keyboards import *
import requests
from bs4 import BeautifulSoup

bot = TeleBot(TOKEN, parse_mode='HTML')  # Регистрация бота и брать СТИЛИ как в HTML


@bot.message_handler(commands=['start', 'help', 'history'])  # Декоратор
def command_start(message):
    chat_id = message.chat.id
    if message.text == '/start':
        msg = bot.send_message(chat_id, f'''Привет, <b>{message.from_user.first_name}</b>
Я - Бот перевода и определения слов и текста''',
                               reply_markup=generate_phone_number())  # обернули сообщение в переменную MSG
        cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (chat_id,))
        user = cursor.fetchone()
        if user:
            bot.send_message(chat_id, 'Что желаете сделать?', reply_markup=choose_command())
        else:
            bot.register_next_step_handler(msg, register_user)
    # TODO сделать функцию РЕГИСТРАЦИИ

    elif message.text == '/help':
        bot.send_message(chat_id, f'''Данные Бот был создан при поддержке <b>PROWEB</b>
При создании бота ни один студент не пострадал
Если у Вас есть вопросы или что-то сломалось
Пишите сюда: @Irmatov''')
    elif message.text == '/history':
        bot.send_message(chat_id, user_history)


def register_user(message):
    chat_id = message.chat.id
    try:
        first_name = message.from_user.first_name
        username = message.from_user.username
        phone = message.contact.phone_number

        cursor.execute('''
        INSERT INTO users(telegram_id, first_name, username, phone) VALUES
        (?,?,?,?);
        ''', (chat_id, first_name, username, phone))
        db.commit()
        msg = bot.send_message(chat_id, 'Что желаете сделать?', reply_markup=choose_command())

    except:
        msg = bot.send_message(chat_id, 'НАЖМИТЕ НА КНОПКУ!!!', reply_markup=generate_phone_number())
        bot.register_next_step_handler(msg, register_user())


@bot.message_handler(regexp=r'Перевод \U0001F913')  # Реакция на текст
def translate_start(message):
    chat_id = message.chat.id
    word = bot.send_message(chat_id, 'Введите слово или текст, которые Вы хотите перевести!')
    bot.register_next_step_handler(word, translation)


@bot.message_handler(regexp=r'Определение \U0001F9D0')  # Реакция на текст
def definition_start(message):
    chat_id = message.chat.id
    word = bot.send_message(chat_id, 'Введите слово, определение которого Вы хотите знать!')
    bot.register_next_step_handler(word, wikipedia_answer)


def translation(message):
    chat_id = message.chat.id
    word = message.text
    if word in ['\start', '\help', '\history', 'Определение \U0001f9D0']:
        if word == 'Определение \U0001f9D0':
            definition_start(message)
        else:
            command_start(message)
    else:
        translator = Translator()
        english_word = translator.translate(word, dest='en').text
        print(english_word)
        cursor.execute('''
        SELECT user_id FROM users WHERE telegram_id = ?;
        ''', (chat_id,))
        user_id = cursor.fetchone()[0]
        cursor.execute('''
        INSERT INTO history_translation(user_id, user_text, translate_text) VALUES
        (?,?,?)
    ''', (user_id, word, english_word))
        db.commit()
        bot.send_message(chat_id, english_word)
        translate_start(
            message)  # чтобы не могли переключиться и выключить нижнюю строку с автовопросом ЧТО ДЕЛАТЬ ДАЛЕЕ ЦИКЛИРУЕМ
        # msg = bot.send_message(chat_id, 'Что желаете сделать?', reply_markup=choose_command())


def wikipedia_answer(message):
    word = message.text
    chat_id = message.chat.id
    if word in ['/start', '/help', '/history',
                'Перевод \U0001F913']:  # защита от переводаи или определения для КОМАНД Телеграмм
        if word == 'Перевод \U0001F913':
            translate_start(message)
        else:
            command_start(message)
    else:
        full_url = f'https://ru.wikipedia.org/wiki/{word}'
        print(full_url)
        html = requests.get(full_url).text
        soup = BeautifulSoup(html, 'html.parser')
        print(soup)
        definition = soup.find('p').get_text(strip=True)

        cursor.execute('''
        SELECT user_id from users WHERE telegram_id = ?;
        ''', (chat_id,))
        user_id = cursor.fetchone()[0]
        cursor.execute('''
        INSERT INTO history_definition(user_id, user_text, definition_text) VALUES
        (?, ?, ?)
        ''', (user_id, word, definition))
        db.commit()
        bot.send_message(chat_id, definition)
        definition_start(message)

def user_history(message):
    chat_id = message.chat.id





bot.polling(none_stop=True)  # Работает бесконечно
