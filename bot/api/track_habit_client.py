import logging
from typing import Any

from bot.database.database import User
from config_data.config import API_URL
from requests import get, patch, post
from requests.models import Response

from api.authentication import ExpiredTokenError, refresh_token, refresh_token_decorator

logger = logging.getLogger(__name__)


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
    logger.info(
        "track_habit_get_all_api request, telegram_id=%s",
        user.telegram_id,
    )

    response: Response = get(f"{API_URL}/api/habits_tracing", headers=headers)
    result: dict = response.json()
    logger.debug(
        "track_habit_get_all_api response, telegram_id=%s, status=%s",
        user.telegram_id,
        response.status_code,
    )

    if response.status_code == 200:
        logger.info(
            "track_habit_get_all_api success, telegram_id=%s, habits_count=%s",
            user.telegram_id,
            len(result["habits"]),
        )
        return result["habits"]

    elif response.status_code == 401:
        logger.warning(
            "track_habit_get_all_api unauthorized (401), telegram_id=%s",
            user.telegram_id,
        )
        raise ExpiredTokenError(user=user)

    logger.error(
        "track_habit_get_all_api failed, telegram_id=%s, status=%s, error_message=%r",
        user.telegram_id,
        response.status_code,
        response.text,
    )
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

    logger.info(
        "track_habit_check_api request, telegram_id=%s, habit_id=%s",
        user.telegram_id,
        habit_id,
    )

    response: Response = post(
        f"{API_URL}/api/habits_tracing/check", headers=headers, json=json_data
    )
    logger.debug(
        "track_habit_check_api response, telegram_id=%s, habit_id=%s, status=%s",
        user.telegram_id,
        habit_id,
        response.status_code,
    )

    if response.status_code == 200:
        logger.info(
            "track_habit_check_api success, telegram_id=%s, habit_id=%s",
            user.telegram_id,
            habit_id,
        )
        return True
    elif response.status_code == 401:
        logger.warning(
            "track_habit_check_api unauthorized (401), telegram_id=%s, habit_id=%s",
            user.telegram_id,
            habit_id,
        )
        raise ExpiredTokenError(user=user)

    logger.error(
        "track_habit_check_api failed, telegram_id=%s, habit_id=%s, status=%s, error_message=%r",
        user.telegram_id,
        habit_id,
        response.status_code,
        response.text,
    )
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
    logger.info(
        "track_habit_get_stats_all request, telegram_id=%s",
        user.telegram_id,
    )

    response: Response = get(
        f"{API_URL}/api/habits_tracking/statistic", headers=headers
    )
    logger.debug(
        "track_habit_get_stats_all response, telegram_id=%s, status=%s",
        user.telegram_id,
        response.status_code,
    )

    if response.status_code == 200:
        habits = response.json().get("habits") or []
        logger.info(
            "track_habit_get_stats_all success, telegram_id=%s, habits_count=%s",
            user.telegram_id,
            len(habits),
        )
        return habits
    elif response.status_code == 401:
        logger.warning(
            "track_habit_get_stats_all unauthorized (401), telegram_id=%s",
            user.telegram_id,
        )
        raise ExpiredTokenError(user=user)

    logger.error(
        "track_habit_get_stats_all failed, telegram_id=%s, status=%s, error_message=%r",
        user.telegram_id,
        response.status_code,
        response.text,
    )
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
    logger.info(
        "track_habit_get_stats request, telegram_id=%s, habit_id=%s",
        user.telegram_id,
        habit_id,
    )

    response: Response = get(
        f"{API_URL}/api/habits_tracking/statistic/{habit_id}", headers=headers
    )
    logger.debug(
        "track_habit_get_stats response, telegram_id=%s, habit_id=%s, status=%s",
        user.telegram_id,
        habit_id,
        response.status_code,
    )

    if response.status_code == 200:
        habits = response.json().get("habits") or []
        logger.info(
            "track_habit_get_stats success, telegram_id=%s, habit_id=%s, data_points=%s",
            user.telegram_id,
            habit_id,
            len(habits),
        )
        return habits
    elif response.status_code == 401:
        logger.warning(
            "track_habit_get_stats unauthorized (401), telegram_id=%s, habit_id=%s",
            user.telegram_id,
            habit_id,
        )
        raise ExpiredTokenError(user=user)

    logger.error(
        "track_habit_get_stats failed, telegram_id=%s, habit_id=%s, status=%s, error_message=%r",
        user.telegram_id,
        habit_id,
        response.status_code,
        response.text,
    )
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
    alert_time = f"{hour}:{minute}"
    json_data: dict[str, str] = {
        "habit_id": habit_id,
        "alert_time": alert_time,
    }

    logger.info(
        "track_habit_set_alert_time request, telegram_id=%s, habit_id=%s, alert_time=%s",
        user.telegram_id,
        habit_id,
        alert_time,
    )

    response: Response = patch(
        f"{API_URL}/api/habits_tracking/alert_time", headers=headers, json=json_data
    )
    logger.debug(
        "track_habit_set_alert_time response, telegram_id=%s, habit_id=%s, status=%s",
        user.telegram_id,
        habit_id,
        response.status_code,
    )

    if response.status_code == 200:
        logger.info(
            "track_habit_set_alert_time success, telegram_id=%s, habit_id=%s, alert_time=%s",
            user.telegram_id,
            habit_id,
            alert_time,
        )
        return True
    elif response.status_code == 401:
        logger.warning(
            "track_habit_set_alert_time unauthorized (401), telegram_id=%s, habit_id=%s",
            user.telegram_id,
            habit_id,
        )
        raise ExpiredTokenError(user=user)

    logger.error(
        "track_habit_set_alert_time failed, telegram_id=%s, habit_id=%s, status=%s, error_message=%r",
        user.telegram_id,
        habit_id,
        response.status_code,
        response.text,
    )
    return False
