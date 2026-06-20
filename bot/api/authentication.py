from typing import Callable, Any
from functools import wraps
from config_data.config import API_URL
from requests import post
from requests.models import Response
from bot.database.models import update_user_tokens, get_user_by_telegram_id
from bot.database.database import User


class ExpiredTokenError(Exception):
    """Возникает, когда токен доступа истек и требует обновления."""

    def __init__(self, user: "User", original_token: str | None = None):
        self.user = user
        self.original_token = original_token
        super().__init__(f"Token expired for user {user.telegram_id}")


def registration_user(telegram_id: int, username: str, password: str) -> bool:
    """
    Функция регистрации пользователя в API

    :param telegram_id: Телеграм ID пользователя
    :type telegram_id: int
    :param username: Имя пользователя в телеграмме
    :type username: str
    :param password: Пароль пользователя
    :type password: str
    :return: True or False
    :rtype: bool
    """

    json_data: dict[str, str | int] = {
        "telegram_id": telegram_id,
        "username": username,
        "password": password,
    }
    response: Response = post(f"{API_URL}/api/auth/login", json=json_data)
    if response.status_code == 200:
        return True
    else:
        return False


def get_token(username: str, password: str) -> dict[str, str] | None:
    """
    Функция для получения токена из API по логину и паролю

    :param username: Имя пользователя в телеграмме
    :type username: str
    :param password: Пароль пользователя
    :type password: str
    :return: Словарь с токенами | Ничего
    :rtype: dict[str, str] | None
    """

    from_data: dict[str, str | int] = {
        "username": username,
        "password": password,
    }
    response: Response = post(f"{API_URL}/api/auth/token", data=from_data)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def refresh_token(token: str):
    json_data: dict[str, str] = {
        "refresh_token": token,
    }
    response: Response = post(f"{API_URL}/api/auth/refresh_token", json=json_data)
    return response.json()


def refresh_token_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    """Повторяет вызов функции при ошибке 401 с предварительным обновлением токена.

    Если результат функции равен `401`, декоратор:
      - извлекает пользователя из `kwargs["user"]`;
      - обновляет его токены через `refresh_token` и `update_user_tokens`;
      - заменяет пользователя в `kwargs` на актуальную версию из БД;
      - вызывает функцию повторно.

    Требования:
      - `func` должна возвращать `401` при ошибке авторизации.
      - в `kwargs` должен быть ключ `"user"` с объектом `User`, имеющим `.to_json()`.

    Поведение:
      - выполняется только одна повторная попытка;
      - ошибки на этапе обновления токена подавляются (возвращается исходный 401);
      - `kwargs` изменяются «на месте».

    Args:
        func: Функция для декорирования.

    Returns:
        Функция-обертка с той же сигнатурой.
    """

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except ExpiredTokenError as exc:
            user: User = kwargs.get("user")
            api_token_refresh: str = user.to_json().get("api_token_refresh")
            tokens: dict[str, str] = refresh_token(token=api_token_refresh)

            update_user_tokens(telegram_id=user.telegram_id, token_data=tokens)

            new_user: User = get_user_by_telegram_id(telegram_id=user.telegram_id)
            kwargs["user"] = new_user
            result = func(*args, **kwargs)
        return result

    return wrapped_func
