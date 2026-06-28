from typing import Any

from bot.database.database import User
from config_data.config import API_URL
from requests import get, patch, post
from requests.models import Response

from api.authentication import ExpiredTokenError, refresh_token, refresh_token_decorator


@refresh_token_decorator
def track_habit_get_all_api(user: User) -> list[dict[str, Any]] | None:
    """
    Получить все отслеживаемые привычки.

    Args:
        user: Пользователь User.

    Returns:
        Список содержащий привычки с отслеживанием.
        Либо None.

    Raises:
        ExpiredTokenError: В случае 401 ошибки (невалидный токен).
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }

    response: Response = get(f"{API_URL}/api/habits_tracing", headers=headers)
    result: dict = response.json()

    if response.status_code == 200:
        return result["habits"]

    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return None


@refresh_token_decorator
def track_habit_check_api(user: User, habit_id: int) -> bool:
    """
    Поставить отметку о выполнении привычки.

    Args:
        user: Пользователь User.
        habit_id: ID привычки.

    Returns:
        True в случае успеха.
        False не удалось поставить отметку о выполнении привычки.

    Raises:
        ExpiredTokenError: В случае 401 ошибки (невалидный токен).
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }
    json_data: dict[str, int] = {
        "habit_id": habit_id,
    }

    response: Response = post(
        f"{API_URL}/api/habits_tracing/check", headers=headers, json=json_data
    )

    if response.status_code == 200:
        return True
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return False


@refresh_token_decorator
def track_habit_get_stats_all(user: User) -> list[dict[str, str]] | None:
    """
    Получить полную статистику о выполнении привычек.

    Args:
        user: Пользователь User.

    Returns:
        Список привычек со статистикой их выполнения.
        None не удалось получить статистику о выполнении привычек.

    Raises:
        ExpiredTokenError: В случае 401 ошибки (невалидный токен).
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }

    response: Response = get(
        f"{API_URL}/api/habits_tracking/statistic", headers=headers
    )

    if response.status_code == 200:
        return response.json()["habits"]
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return None


@refresh_token_decorator
def track_habit_get_stats(user: User, habit_id: int) -> list[dict[str, str]] | None:
    """
    Получить полную статистику о выполнении одной привычки.

    Args:
        user: Пользователь User.
        habit_id: ID привычки.

    Returns:
        Список из одной привычки со статистикой её выполнения.
        None не удалось получить статистику о выполнении привычки.

    Raises:
        ExpiredTokenError: В случае 401 ошибки (невалидный токен).
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }

    response: Response = get(
        f"{API_URL}/api/habits_tracking/statistic/{habit_id}", headers=headers
    )

    if response.status_code == 200:
        return response.json()["habits"]
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return None


@refresh_token_decorator
def track_habit_set_alert_time(user: User, habit_id: int, hour, minute) -> bool:
    """
    Поставить отметку о выполнении привычки.

    Args:
        user: Пользователь User.
        habit_id: ID привычки.
        hour: Время в формате hh.
        minute: Минуты в формате mm.

    Returns:
        True в случае успеха.
        False не удалось поставить отметку о выполнении привычки.

    Raises:
        ExpiredTokenError: В случае 401 ошибки (невалидный токен).
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }
    json_data: dict[str, str] = {
        "habit_id": habit_id,
        "alert_time": f"{hour}:{minute}",
    }

    response: Response = patch(
        f"{API_URL}/api/habits_tracking/alert_time", headers=headers, json=json_data
    )

    if response.status_code == 200:
        return True
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return False
