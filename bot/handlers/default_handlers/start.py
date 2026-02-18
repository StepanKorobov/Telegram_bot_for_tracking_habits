from telebot.types import Message

from bot.database.database import User
from database.models import get_user_by_telegram_id, with_current_user
from loader import bot
from states.login import LoginState

# @bot.message_handler(commands=["start"])
# def bot_start(message: Message):
#     bot.reply_to(message, f"Привет, {message.from_user.full_name}!")


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    """Функция начала взаимодействия с ботом, проверяет зарегистрирован ли пользователь"""

    user: User | None = get_user_by_telegram_id(telegram_id=message.from_user.id)

    if user is None:
        bot.send_message(
            message.from_user.id,
            f"Привет {message.from_user.full_name}, ты ещё не зарегистрирован! Для регистрации введи пароль:",
        )
        bot.set_state(message.from_user.id, LoginState.registration, message.chat.id)
    else:
        bot.send_message(
            message.from_user.id, f"Привет, {message.from_user.full_name}!"
        )
