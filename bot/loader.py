from telebot import TeleBot, apihelper
from telebot.storage import StateMemoryStorage

from bot.database.database import Base, engine
from config_data import config

if config.PROXY:
    apihelper.proxy = {
        "https": f"socks5h://{config.PROXY}",
        "http": f"socks5h://{config.PROXY}",
    }

Base.metadata.create_all(bind=engine)
storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
