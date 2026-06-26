import datetime

from bot.database.database import User
from config_data.config import API_URL
from requests import get, post, patch
from requests.models import Response

from api.authentication import ExpiredTokenError, refresh_token, refresh_token_decorator


@refresh_token_decorator
def track_habit_get_all_api(user: User):
    """
    Функция для отметки выполнения привычки через API

    :param user: Пользователь
    :type user: User
    :return: True or False
    :rtype: bool
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }

    response: Response = get(
        f"{API_URL}/api/habits_tracing", headers=headers
    )
    result: dict = response.json()

    if response.status_code == 200:
        return result["result"]

    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return False


@refresh_token_decorator
def track_habit_check_api(user: User, habit_id: int) -> bool:
    """
    Функция для отметки выполнения привычки через API

    :param user: Пользователь
    :type user: User
    :param habit_id: ID привычки для удаления
    :type habit_id: int
    :return: True or False
    :rtype: bool
    """

    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }
    data: dict[str, int] = {
        "habit_id": habit_id,
    }

    response: Response = post(
        f"{API_URL}/api/habits_tracing/check", headers=headers, json=data
    )

    if response.status_code == 200:
        return True
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return False


@refresh_token_decorator
def track_habit_get_stats_all(user: User) -> list[dict[str, str]] | None:
    """
    Функция для получения статистики выполнений всех привычек через API

    :param user: Пользователь
    :type user: User
    :return: Список словарей со статистикой привычек
    :rtype: list[dict[str, str]] | None
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
    Функция для получения статистики выполнений одной привычки через API

    :param user: Пользователь
    :type user: User
    :param habit_id: ID привычки для удаления
    :type habit_id: int
    :return: Список со словарём содержащим статистику о привычке
    :rtype: list[dict[str, str]] | None
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
def track_habit_set_alert_time(user: User, habit_id: int, hour, minute) -> bool | None:
    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }
    data: dict[str, str] = {
        "habit_id": habit_id,
        "alert_time": f"{hour}:{minute}",
    }

    response: Response = patch(
        f"{API_URL}/api/habits_tracking/alert_time", headers=headers, json=data
    )

    if response.status_code == 200:
        return True
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return None
