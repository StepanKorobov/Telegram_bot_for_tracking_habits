"""Файл конфигурации, загрузки переменных окружения, дефолтных значений, настройка логов"""

import os

from dotenv import find_dotenv, load_dotenv

from logging_config import setup_logging
import logging
setup_logging()
logger = logging.getLogger(__name__)
logger.info("Service started")

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

API_URL: str = "http://127.0.0.1:8000"
BOT_TOKEN: str = os.getenv("BOT_TOKEN")
API_KEY: str = os.getenv("API_KEY")
PROXY: str = os.getenv("PROXY")
URL: str = ""
DEFAULT_COMMANDS: tuple = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("login", "Залогиниться в бота"),
    ("add_habit", "Добавить привычку"),
    ("habit", "Посмотреть все привычки"),
    ("edit_habit", "Редактирование привычек"),
    ("track_habit", "Отметить выполнение привычек"),
    ("habit_stats", "Получение статистики по выполнению привычек"),
    ("set_reminder", "Установить напоминание по выполнению привычек")
)
path: str = os.path.abspath("log/debug.log")  # путь папки с логами
# конфигурация логов
