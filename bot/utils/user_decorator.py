from functools import wraps
from typing import Any, Callable

from api.authentication import TokenRefreshFailed
from bot.database.database import User
from bot.database.models import check_user_by_telegram_id, get_user_by_telegram_id
from loader import bot
from states.login import LoginState


def with_current_user(func: Callable) -> Callable:
    """Декоратор для получения текущего пользователя"""

    @wraps(func)
    def wrapper(message, *args, **kwargs) -> Any:
        user_id: int = message.from_user.id
        chat_id: int = message.chat.id
        full_name: str = message.from_user.full_name

        current_user: User | None = get_user_by_telegram_id(telegram_id=user_id)

        # Можно ещё положить db
        if current_user:
            try:
                result = func(message, current_user=current_user, *args, **kwargs)
            except TokenRefreshFailed as exc:
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
                return result
        else:
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
        current_user: User = get_user_by_telegram_id(telegram_id=call.from_user.id)
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

        user_exist: bool = check_user_by_telegram_id(telegram_id=user_id)
        if user_exist:
            # return func(message, current_user=current_user, *args, **kwargs)
            return func(message, *args, **kwargs)

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
