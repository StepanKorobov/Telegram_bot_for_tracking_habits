from dotenv import find_dotenv, load_dotenv
from envparse import env
import os

from celery import Celery
import telebot

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BOT_TOKEN = env("BOT_TOKER")
bot = telebot.TeleBot(BOT_TOKEN)

app = Celery(
    "myapp",
    broker=redis_url,
    backend=redis_url,
    include=["tasks"],
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
