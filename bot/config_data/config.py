"""Файл конфигурации, загрузки переменных окружения, дефолтных значений, настройка логов"""

import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
URL = ""
DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку")
)
path = os.path.abspath("log/debug.log")  # путь папки с логами
# конфигурация логов
