from api.authentication import get_token, registration_user
from bot.database.models import update_user_tokens
from database.models import add_user, check_user_by_telegram_id, get_user_by_telegram_id
from loader import bot
from states.login import LoginState
from telebot.types import Message
from utils.password_validation import password_validator


@bot.message_handler(commands=["login"])
def login(message: Message) -> None:
    """
    Команда входа в бота.

    Args:
        message: Сообщение с данными.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id

    user: bool = check_user_by_telegram_id(telegram_id=user_id)

    if user:
        bot.set_state(
            user_id=user_id,
            state=LoginState.login,
            chat_id=chat_id,
        )
        text = "Для входа в бота введите пароль:"
    else:
        bot.set_state(
            user_id=user_id,
            state=LoginState.registration,
            chat_id=chat_id,
        )
        text = "Для регистрации введите пароль:"

    bot.send_message(
        chat_id=chat_id,
        text=text,
    )


@bot.message_handler(state=LoginState.login)
def login(message: Message) -> None:
    """
    Вход пользователя в бота.

    Args:
        message: Сообщение с данными.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id
    message_id: int = message.message_id
    username: str = message.from_user.username

    bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )

    password: str = message.text
    user = get_user_by_telegram_id(telegram_id=user_id)
    tokens = get_token(
        username=username,
        password=password,
    )

    if tokens:
        update_user_tokens(
            telegram_id=user_id,
            token_data=tokens,
        )
        bot.send_message(
            chat_id=chat_id,
            text=f"Привет {message.from_user.username}, вы успешно вошли в бота",
        )
        bot.delete_state(
            user_id=user_id,
            chat_id=chat_id,
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text=f"Ошибка: Не верный пароль. Введите пароль:",
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
def registration(message: Message) -> None:
    """
    Регистрация пользователя в боте.

    Args:
        message: Сообщение с данными.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id
    message_id: int = message.message_id
    username: str = message.from_user.username

    bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )

    password: str = message.text
    check_password: bool = password_validator(password=password)

    if check_password:
        reg: bool = registration_user(
            telegram_id=user_id,
            username=username,
            password=password,
        )
        tokens: dict[str:str] = get_token(
            username=username,
            password=password,
        )
        add_user(
            telegram_id=user_id,
            username=username,
            api_token=tokens["access_token"],
            api_token_refresh=tokens["refresh_token"],
        )
        bot.send_message(
            chat_id=chat_id,
            text="Регистрация успешна!",
        )
        bot.delete_state(
            user_id=user_id,
            chat_id=chat_id,
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Ошибка: Пароль должен содержать только буквы латинского алфавита и цифры. Введите пароль:",
        )
