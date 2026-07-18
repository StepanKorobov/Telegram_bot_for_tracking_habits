import logging

from api.authentication import get_token, registration_user
from bot.database.database import User
from bot.database.models import update_user_tokens
from database.models import add_user, check_user_by_telegram_id, get_user_by_telegram_id
from loader import bot
from states.login import LoginState
from telebot.types import Message
from utils.password_validation import password_validator

logger = logging.getLogger(__name__)


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
    username: str = message.from_user.username

    logger.info(
        "command /login, user_id=%s, chat_id=%s, username=%r",
        user_id,
        chat_id,
        username,
    )

    user_exists: bool = check_user_by_telegram_id(telegram_id=user_id)

    logger.debug(
        "user existence check, user_id=%s, exists=%s",
        user_id,
        user_exists,
    )
    if user_exists:
        bot.set_state(
            user_id=user_id,
            state=LoginState.login,
            chat_id=chat_id,
        )
        text = "Для входа в бота введите пароль:"
        logger.info(
            "user will login, user_id=%s, chat_id=%s",
            user_id,
            chat_id,
        )
    else:
        bot.set_state(
            user_id=user_id,
            state=LoginState.registration,
            chat_id=chat_id,
        )
        text = "Для регистрации введите пароль:"
        logger.info(
            "user will register, user_id=%s, chat_id=%s",
            user_id,
            chat_id,
        )

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

    logger.info(
        "login attempt, user_id=%s, chat_id=%s, username=%r",
        user_id,
        chat_id,
        username,
    )

    bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )

    password: str = message.text
    user: User | None = get_user_by_telegram_id(telegram_id=user_id)

    logger.debug(
        "user loaded for login, user_id=%s, user_db=%r",
        user_id,
        bool(user),
    )

    tokens = get_token(
        username=username,
        password=password,
    )

    if tokens:
        logger.info(
            "login success, user_id=%s, username=%r",
            user_id,
            username,
        )
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
        logger.warning(
            "login failed: invalid password, user_id=%s, username=%r",
            user_id,
            username,
        )
        bot.send_message(
            chat_id=chat_id,
            text=f"Ошибка: Не верный пароль. Введите пароль:",
        )


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

    logger.info(
        "registration attempt, user_id=%s, chat_id=%s, username=%r",
        user_id,
        chat_id,
        username,
    )

    bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )

    password: str = message.text
    check_password: bool = password_validator(password=password)

    logger.debug(
        "password validation result, user_id=%s, valid=%s",
        user_id,
        check_password,
    )

    if check_password:
        try:
            reg: bool = registration_user(
                telegram_id=user_id,
                username=username,
                password=password,
            )
            logger.info(
                "registration API result, user_id=%s, username=%r, success=%s",
                user_id,
                username,
                reg,
            )
            tokens: dict[str:str] = get_token(
                username=username,
                password=password,
            )
            logger.debug(
                "token retrieval after registration, user_id=%s, has_tokens=%s",
                user_id,
                bool(tokens),
            )
            add_user(
                telegram_id=user_id,
                username=username,
                api_token=tokens["access_token"],
                api_token_refresh=tokens["refresh_token"],
            )
            logger.info(
                "user stored locally after registration, user_id=%s, username=%r",
                user_id,
                username,
            )
            bot.send_message(
                chat_id=chat_id,
                text="Регистрация успешна!",
            )
            bot.delete_state(
                user_id=user_id,
                chat_id=chat_id,
            )
        except Exception as exc:
            logger.exception(
                "registration flow failed, user_id=%s, username=%r, exc=%r",
                user_id,
                username,
                exc,
            )
            bot.send_message(
                chat_id=chat_id,
                text="Произошла ошибка при регистрации. Попробуйте позже.",
            )
    else:
        logger.warning(
            "registration failed: weak/invalid password, user_id=%s, username=%r",
            user_id,
            username,
        )
        bot.send_message(
            chat_id=chat_id,
            text="Ошибка: Пароль должен содержать только буквы латинского алфавита и цифры. Введите пароль:",
        )
