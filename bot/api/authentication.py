from functools import wraps
from typing import Any, Callable

from bot.database.database import User
from bot.database.models import get_user_by_telegram_id, update_user_tokens
from config_data.config import API_URL
from requests import post
from requests.models import Response


class ExpiredTokenError(Exception):
    """Возникает, когда токен доступа истек и требует обновления."""

    def __init__(self, user: "User"):
        self.user = user
        super().__init__(f"Token expired for user {user.telegram_id}")


class TokenRefreshFailed(Exception):
    """Возникает, когда токен не удалось обновить и требуется, что бы пользователь залогинился"""

    def __init__(self, user: "User"):
        self.user = user
        super().__init__(f"Failed token update for user {user.telegram_id}")


def registration_user(telegram_id: int, username: str, password: str) -> bool | None:
    """
    Регистрация пользователя по логину, паролю, telegram ID

    Args:
        telegram_id: Telegram ID пользователя.
        username: Имя пользователя в telegram.
        password: Пароль введённый пользователем.

    Returns:
        True случае успеха, None  случае неуспешной регистрации.
    """

    json_data: dict[str, str | int] = {
        "telegram_id": telegram_id,
        "username": username,
        "password": password,
    }
    response: Response = post(f"{API_URL}/api/auth/login", json=json_data)
    if response.status_code == 200:
        return True
    return None


def get_token(username: str, password: str) -> dict[str, str] | None:
    """
    Получение access и refresh токенов по логину и паролю.

    Args:
        username: Имя пользователя в telegram.
        password: Пароль введённый пользователем.

    Returns:
        Словарь содержащий токены и их тип.
        None в случае неуспешного запроса.
    """

    form_data: dict[str, str | int] = {
        "username": username,
        "password": password,
    }
    response: Response = post(f"{API_URL}/api/auth/token", data=form_data)
    if response.status_code == 200:
        return response.json()
    return None


def refresh_token(token: str) -> dict[str, str] | None:
    """
    Обновление access токена по refresh токену.

    Args:
        token: Access token пользователя.

    Returns:
        Словарь содержащий токены и их тип.
        None в случае неуспешного запроса.
    """

    json_data: dict[str, str] = {
        "refresh_token": token,
    }
    response: Response = post(f"{API_URL}/api/auth/refresh_token", json=json_data)
    if response.status_code == 200:
        return response.json()
    return None


def refresh_token_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Декоратор для автоматического обновления истёкшего API‑токена в случае 401 статуса при обращении к API.

    Логика работы:
        1. Вызывает декорируемую функцию.
        2. Если возникает ExpiredTokenError, пытается обновить токен через refresh‑токен пользователя.
        3. При успешном обновлении повторяет вызов функции с обновлённым объектом `user`.
        4. Если обновление снова вызывает ExpiredTokenError (например, refresh‑токен тоже истёк),
           отправляет пользователю сообщение о необходимости повторной авторизации и переводит
           его в состояние LoginState.login, затем выбрасывает TokenRefreshFailed.

    Требования к сигнатуре декорируемой функции:
        - Должен присутствовать именованный аргумент `user` типа `User`, через который
          декоратор получает данные для обновления токена.

    Исключения:
        - ValueError: если аргумент `user` отсутствует в вызове.
        - TokenRefreshFailed: если обновить токен не удалось (refresh‑токен недействителен).

    Пример использования:
        @refresh_token_decorator
        def add_habit_api(user: User, habit_data: dict) -> bool:
            ...

    :param func: Функция, требующая валидного API‑токена пользователя.
    :return: Обернутая функция с логикой обновления токена.
    """

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except ExpiredTokenError as exc:
            user: User = kwargs.get("user")

            if not user:
                raise ValueError("user argument is required")

            api_token_refresh: str = user.to_json().get("api_token_refresh")
            tokens: dict[str, str] = refresh_token(token=api_token_refresh)
            update_user_tokens(telegram_id=user.telegram_id, token_data=tokens)
            user: User = get_user_by_telegram_id(telegram_id=user.telegram_id)
            kwargs["user"] = user

            try:
                result = func(*args, **kwargs)
            except ExpiredTokenError as exc:
                raise TokenRefreshFailed(user=user)
            else:
                return result
        else:
            return result

    return wrapped_func
