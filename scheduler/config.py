import logging

from dotenv import find_dotenv, load_dotenv
from envparse import env
from logging_config import setup_logging

logger = logging.getLogger(__name__)

setup_logging()

if not find_dotenv():
    logger.error(".env file not found, environment variables not loaded")
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()
    logger.info(".env file loaded successfully")


BOT_TOKEN = env("BOT_TOKER")
DB_IP = env("DB_IP", default="database")
DB_PORT = env("DB_PORT", default="5432")
DB_USER = env("DB_USER", default="admin")
DB_PASSWORD = env("DB_PASSWORD", default="admin")
DB_DATABASE = env("DB_DATABASE", default="telegram")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_IP}:{DB_PORT}/{DB_DATABASE}"
)

logger.info(
    "config: DATABASE_URL configured for host=%s, port=%s, db=%s, user=%s",
    DB_IP,
    DB_PORT,
    DB_DATABASE,
    DB_USER,
)
