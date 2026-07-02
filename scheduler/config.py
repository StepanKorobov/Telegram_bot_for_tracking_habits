from dotenv import find_dotenv, load_dotenv
from envparse import env

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = env("BOT_TOKER")

DB_IP = env("DB_IP", default="database")
DB_PORT = env("DB_PORT", default="5432")
DB_USER = env("DB_USER", default="admin")
DB_PASSWORD = env("DB_PASSWORD", default="admin")
DB_DATABASE = env("DB_DATABASE", default="telegram")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_IP}:{DB_PORT}/{DB_DATABASE}"
