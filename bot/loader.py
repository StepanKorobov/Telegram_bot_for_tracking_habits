from telebot import TeleBot
from telebot.storage import StateMemoryStorage

from config_data import config
from bot.database.database import Base, engine

Base.metadata.create_all(bind=engine)
storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
