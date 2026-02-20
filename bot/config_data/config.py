"""Файл конфигурации, загрузки переменных окружения, дефолтных значений, настройка логов"""

import os

from dotenv import find_dotenv, load_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

API_URL = "http://127.0.0.1:8000"
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
URL = ""
DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("login", "Залогинится в бота"),
    ("add_habit", "Добавить привычку"),
    ("habit", "Посмотреть все привычки"),
    ("edit_habit", "Редактирование привычек"),
)
path = os.path.abspath("log/debug.log")  # путь папки с логами
# конфигурация логов
