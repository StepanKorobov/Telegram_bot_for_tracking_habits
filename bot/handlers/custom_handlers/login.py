from typing import Dict

from telebot.types import Message

from api.authentication import get_token, registration_user
from database.models import add_user, get_user_by_telegram_id
from loader import bot
from states.login import LoginState
from utils.password_validation import password_validator


@bot.message_handler(commands=["login"])
def login(message: Message):
    user = get_user_by_telegram_id(message.chat.id)
    # bot.set_state(message.from_user.id, LoginState.password, message.chat.id)
    bot.send_message(
        message.from_user.id, f"Привет {message.from_user.username}, Введи пароль:"
    )


# @bot.message_handler(state=LoginState.password)
# def get_password(message: Message):
#     password: str = message.text
#     bot.delete_message(message.chat.id, message.message_id)
#     if password.isalpha():
#         data = {
#             "username": message.from_user.username,
#             "telegram_id": message.from_user.id,
#             "password": password,
#         }
#         result = requests.post("http://127.0.0.1:8000/api/auth/login", json=data)
#         print(result.json())
#         bot.send_message(message.from_user.id, "топ пароль")
#         bot.delete_state(message.from_user.id, message.chat.id)
#     else:
#         bot.send_message(message.from_user.id, "Пароль не удовлетворяет требованиям")


@bot.message_handler(state=LoginState.registration)
def registration(message: Message):
    bot.delete_message(message.chat.id, message.message_id)
    password: str = message.text
    check_password = password_validator(password=password)
    if check_password:
        reg: bool = registration_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            password=password,
        )
        tokens: Dict[str:str] = get_token(
            username=message.from_user.username, password=password
        )
        add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            api_token=tokens["access_token"],
            api_token_refresh=tokens["refresh_token"],
        )
        bot.send_message(message.from_user.id, "Регистрация успешна!")
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(
            message.from_user.id,
            "Ошибка: Пароль должен содержать только буквы латинского алфавита и цифры. Введите пароль:",
        )
