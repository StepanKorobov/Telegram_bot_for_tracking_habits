from datetime import datetime

from bot.database.database import User
from config_data.config import API_URL
from requests import delete, get, patch, post, put
from requests.models import Response

from api.authentication import ExpiredTokenError, refresh_token, refresh_token_decorator


@refresh_token_decorator
def add_habit_api(user: User, habit_data: dict[str, str | datetime]) -> bool:
    """
    Добавить новую привычку.

    Args:
        user: Пользователь User.
        habit_data: Словарь содержащий информацию о привычке.

    Returns:
        True в случае успеха.
        False не удалось добавить привычку.

    Raises:
        ExpiredTokenError: В случае 401 ошибки (невалидный токен).
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }
    data: dict[str, str] = {
        "habit_name": habit_data["name"],
        "description": habit_data["description"],
        "goal": habit_data["goal"],
        "terms_date": habit_data["terms"].strftime("%Y-%m-%d"),
    }

    response: Response = post(f"{API_URL}/api/habits", headers=headers, json=data)

    if response.status_code == 201:
        return True
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return False


@refresh_token_decorator
def get_habit_api(user: User) -> list[dict[str, str | int]] | None:
    """
    Получить все привычки пользователя.

    Args:
        user: Пользователь User.

    Returns:
        Лист привычек в случае успеха.
        None в случе отсутствия привычек.

    Raises:
        ExpiredTokenError: В случае 401 ошибки (невалидный токен).
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }

    response: Response = get(f"{API_URL}/api/habits", headers=headers)
    result: dict = response.json()

    if response.status_code == 200 and result:
        return result["habits"]

    if response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return None


@refresh_token_decorator
def remove_habit_api(user: User, habit_id: int) -> bool | None:
    """
    Удаление одной привычки пользователя.

    Args:
        user: Пользователь User.
        habit_id: ID привычки.

    Returns:
        True в случае успеха.
        False не удалось удалить привычку.

    Raises:
        ExpiredTokenError: В случае 401 ошибки (невалидный токен).
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }

    response: Response = delete(f"{API_URL}/api/habits/{habit_id}", headers=headers)

    if response.status_code == 204:
        return True
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return None


@refresh_token_decorator
def remove_habit_api_all(user: User) -> bool | None:
    """
    Удаление всех привычек пользователя.

    Args:
        user: Пользователь User.

    Returns:
        True в случае успеха.
        False не удалось удалить привычки.

    Raises:
        ExpiredTokenError: В случае 401 ошибки (невалидный токен).
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }

    response: Response = delete(f"{API_URL}/api/habits", headers=headers)

    if response.status_code == 204:
        return True
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return None


@refresh_token_decorator
def edit_habit_api_all(
    user: User, habit_id: int, habit_data: dict[str, str]
) -> bool | None:
    """
    Полное редактирование привычки через API.

    Args:
        user: Пользователь User.
        habit_id: ID привычки.
        habit_data: Словарь содержащий информацию о привычке.

    Returns:
        True в случае успеха.
        False не удалось обновить привычку.

    Raises:
        ExpiredTokenError: В случае 401 ошибки (невалидный токен).
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }
    data = {
        "habit_name": habit_data["name"],
        "description": habit_data["description"],
        "goal": habit_data["goal"],
        "terms_date": habit_data["terms"],
    }

    response = put(f"{API_URL}/api/habits/{habit_id}", headers=headers, json=data)

    if response.status_code == 204:
        return True
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return None


@refresh_token_decorator
def edit_habit_api(
    user: User, habit_id: int, param: str, value: str | int
) -> bool | None:
    """
    Частичное редактирование привычки через API (1 параметр).

    Args:
        user: Пользователь User.
        habit_id: ID привычки.
        param: Параметр, который будем редактировать.
        value: Значение, которое будем вписывать в параметр.

    Returns
        True в случае успеха.
        False не удалось отредактировать привычку.

    Raises:
        ExpiredTokenError: В случае 401 ошибки (невалидный токен).
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }
    data: dict[str, str | int] = {
        param: value,
    }

    response: Response = patch(
        f"{API_URL}/api/habits/{habit_id}", headers=headers, json=data
    )

    if response.status_code == 204:
        return True
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return None
