import sqlite3

db = sqlite3.connect('bot.db', check_same_thread=False) # вырубаем ПОТОКИ которые возникнут из за ошибки - конфликта

cursor = db.cursor()

TOKEN = '5073890459:AAGZGQFkPQE7IOKEBMJ0Nj98lg-lLZTGruw'