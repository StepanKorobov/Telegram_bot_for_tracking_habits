from database.models import check_user_by_telegram_id
from loader import bot
from states.login import LoginState
from telebot.types import Message

# @bot.message_handler(commands=["start"])
# def bot_start(message: Message):
#     bot.reply_to(message, f"Привет, {message.from_user.full_name}!")


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    """
    Функция начала взаимодействия с ботом, проверяет зарегистрирован ли пользователь.

    Args:
        message: Сообщение с данными.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id
    full_name: str = message.from_user.full_name

    user: bool = check_user_by_telegram_id(telegram_id=message.from_user.id)

    if not user:
        bot.send_message(
            chat_id=chat_id,
            text=f"Привет {full_name}, ты ещё не зарегистрирован! Для регистрации введи пароль:",
        )
        bot.set_state(
            user_id=user_id,
            state=LoginState.registration,
            chat_id=chat_id,
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text=f"Привет, {full_name}!",
        )
