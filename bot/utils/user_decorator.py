import logging
from functools import wraps
from typing import Any, Callable

from api.authentication import TokenRefreshFailed
from bot.database.database import User
from bot.database.models import check_user_by_telegram_id, get_user_by_telegram_id
from loader import bot
from states.login import LoginState

logger = logging.getLogger(__name__)


def with_current_user(func: Callable) -> Callable:
    """Декоратор для получения текущего пользователя"""

    @wraps(func)
    def wrapper(message, *args, **kwargs) -> Any:
        user_id: int = message.from_user.id
        chat_id: int = message.chat.id
        full_name: str = message.from_user.full_name

        logger.debug(
            "with_current_user: called for user_id=%s, chat_id=%s, full_name=%r, func=%s",
            user_id,
            chat_id,
            full_name,
            func.__name__,
        )

        current_user: User | None = get_user_by_telegram_id(telegram_id=user_id)

        # Можно ещё положить db
        if current_user:
            logger.debug(
                "with_current_user: user found in DB, telegram_id=%s, username=%r",
                current_user.telegram_id,
                current_user.username,
            )

            try:
                result = func(message, current_user=current_user, *args, **kwargs)
            except TokenRefreshFailed as exc:
                logger.warning(
                    "with_current_user: TokenRefreshFailed, requiring re-login, telegram_id=%s, error_message=%r",
                    current_user.telegram_id,
                    exc,
                )
                bot.send_message(
                    chat_id=chat_id,
                    text=f"Привет {full_name}, ты давно не заходил! Для входа введи пароль:",
                )
                bot.set_state(
                    user_id=user_id,
                    state=LoginState.login,
                    chat_id=chat_id,
                )
            else:
                logger.debug(
                    "with_current_user: handler %s executed successfully for telegram_id=%s",
                    func.__name__,
                    current_user.telegram_id,
                )
                return result
        else:
            logger.info(
                "with_current_user: user not found, switching to registration, user_id=%s",
                user_id,
            )
            bot.send_message(
                chat_id=chat_id,
                text=f"Привет {full_name}, ты ещё не зарегистрирован! Для регистрации введи пароль:",
            )
            bot.set_state(
                user_id=user_id,
                state=LoginState.registration,
                chat_id=chat_id,
            )

    return wrapper


def get_current_user_from_inline_button(func: Callable) -> Callable:
    """Декоратор для получения текущего пользователя, но уже для обработчика кнопки inline"""

    @wraps(func)
    def wrapper(call, *args, **kwargs) -> Any:
        user_id: int = call.from_user.id

        logger.debug(
            "get_current_user_from_inline_button: called for user_id=%s, func=%s",
            user_id,
            func.__name__,
        )

        current_user: User = get_user_by_telegram_id(telegram_id=call.from_user.id)

        if current_user is None:
            logger.error(
                "get_current_user_from_inline_button: user not found in DB, user_id=%s",
                user_id,
            )
        else:
            logger.debug(
                "get_current_user_from_inline_button: user found, telegram_id=%s, username=%r",
                current_user.telegram_id,
                current_user.username,
            )

        return func(call, current_user=current_user, *args, **kwargs)

    return wrapper


def check_user_registration(func) -> Callable:
    """
    Декоратор проверяет зарегистрирован ли пользователь в боте
    """

    @wraps(func)
    def wrapper(message, *args, **kwargs) -> Any:
        user_id: int = message.from_user.id
        chat_id: int = message.chat.id
        full_name: str = message.from_user.full_name

        logger.debug(
            "check_user_registration: called for user_id=%s, func=%s",
            user_id,
            func.__name__,
        )

        user_exist: bool = check_user_by_telegram_id(telegram_id=user_id)
        logger.info(
            "check_user_registration: user_id=%s, exists=%s",
            user_id,
            user_exist,
        )

        if user_exist:
            logger.debug(
                "check_user_registration: user exists, executing handler %s, user_id=%s",
                func.__name__,
                user_id,
            )

            # return func(message, current_user=current_user, *args, **kwargs)
            return func(message, *args, **kwargs)

        logger.info(
            "check_user_registration: user not registered, switching to registration, "
            "user_id=%s",
            user_id,
        )

        bot.send_message(
            message.from_user.id,
            f"Привет {full_name}, ты ещё не зарегистрирован! Для регистрации введи пароль:",
        )
        bot.set_state(
            user_id=user_id,
            state=LoginState.registration,
            chat_id=chat_id,
        )

    return wrapper
