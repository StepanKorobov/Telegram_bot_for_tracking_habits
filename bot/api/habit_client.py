import logging
from datetime import datetime

from bot.database.database import User
from config_data.config import API_URL
from requests import delete, get, patch, post, put
from requests.models import Response

from api.authentication import ExpiredTokenError, refresh_token, refresh_token_decorator

logger = logging.getLogger(__name__)


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

    logger.info(
        "add_habit_api request, telegram_id=%s, habit_name=%r, goal=%r, terms_date=%s",
        user.telegram_id,
        data["habit_name"],
        data["goal"],
        data["terms_date"],
    )

    response: Response = post(f"{API_URL}/api/habits", headers=headers, json=data)
    logger.debug(
        "add_habit_api response, telegram_id=%s, status=%s",
        user.telegram_id,
        response.status_code,
    )

    if response.status_code == 201:
        logger.info(
            "add_habit_api success, telegram_id=%s, habit_name=%r",
            user.telegram_id,
            data["habit_name"],
        )
        return True
    elif response.status_code == 401:
        logger.warning(
            "add_habit_api unauthorized (401), telegram_id=%s",
            user.telegram_id,
        )
        raise ExpiredTokenError(user=user)

    logger.error(
        "add_habit_api failed, telegram_id=%s, status=%s, error_message=%r",
        user.telegram_id,
        response.status_code,
        response.text,
    )
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

    logger.info(
        "get_habit_api request, telegram_id=%s",
        user.telegram_id,
    )

    response: Response = get(f"{API_URL}/api/habits", headers=headers)
    logger.debug(
        "get_habit_api response, telegram_id=%s, status=%s",
        user.telegram_id,
        response.status_code,
    )

    result: dict = response.json()

    if response.status_code == 200 and result:
        logger.info(
            "get_habit_api success, telegram_id=%s, habits_count=%s",
            user.telegram_id,
            len(result["habits"]),
        )

        return result["habits"]

    if response.status_code == 401:
        logger.warning(
            "get_habit_api unauthorized (401), telegram_id=%s",
            user.telegram_id,
        )
        raise ExpiredTokenError(user=user)

    logger.error(
        "get_habit_api failed, telegram_id=%s, status=%s, error_message=%r",
        user.telegram_id,
        response.status_code,
        response.text,
    )
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
    logger.info(
        "remove_habit_api request, telegram_id=%s, habit_id=%s",
        user.telegram_id,
        habit_id,
    )

    response: Response = delete(f"{API_URL}/api/habits/{habit_id}", headers=headers)
    logger.debug(
        "remove_habit_api response, telegram_id=%s, habit_id=%s, status=%s",
        user.telegram_id,
        habit_id,
        response.status_code,
    )

    if response.status_code == 204:
        logger.info(
            "remove_habit_api success, telegram_id=%s, habit_id=%s",
            user.telegram_id,
            habit_id,
        )
        return True
    elif response.status_code == 401:
        logger.warning(
            "remove_habit_api unauthorized (401), telegram_id=%s, habit_id=%s",
            user.telegram_id,
            habit_id,
        )
        raise ExpiredTokenError(user=user)

    logger.error(
        "remove_habit_api failed, telegram_id=%s, habit_id=%s, status=%s, error_message=%r",
        user.telegram_id,
        habit_id,
        response.status_code,
        response.text,
    )
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
    logger.info(
        "remove_habit_api_all request, telegram_id=%s",
        user.telegram_id,
    )

    response: Response = delete(f"{API_URL}/api/habits", headers=headers)
    logger.debug(
        "remove_habit_api_all response, telegram_id=%s, status=%s",
        user.telegram_id,
        response.status_code,
    )

    if response.status_code == 204:
        logger.info(
            "remove_habit_api_all success, telegram_id=%s",
            user.telegram_id,
        )
        return True
    elif response.status_code == 401:
        logger.warning(
            "remove_habit_api_all unauthorized (401), telegram_id=%s",
            user.telegram_id,
        )
        raise ExpiredTokenError(user=user)

    logger.error(
        "remove_habit_api_all failed, telegram_id=%s, status=%s, error_message=%r",
        user.telegram_id,
        response.status_code,
        response.text,
    )
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

    logger.info(
        "edit_habit_api_all request, telegram_id=%s, habit_id=%s, habit_name=%r",
        user.telegram_id,
        habit_id,
        data["habit_name"],
    )

    response = put(f"{API_URL}/api/habits/{habit_id}", headers=headers, json=data)
    logger.debug(
        "edit_habit_api_all response, telegram_id=%s, habit_id=%s, status=%s",
        user.telegram_id,
        habit_id,
        response.status_code,
    )

    if response.status_code == 204:
        logger.info(
            "edit_habit_api_all success, telegram_id=%s, habit_id=%s",
            user.telegram_id,
            habit_id,
        )
        return True
    elif response.status_code == 401:
        logger.warning(
            "edit_habit_api_all unauthorized (401), telegram_id=%s, habit_id=%s",
            user.telegram_id,
            habit_id,
        )
        raise ExpiredTokenError(user=user)

    logger.error(
        "edit_habit_api_all failed, telegram_id=%s, habit_id=%s, status=%s, error_message=%r",
        user.telegram_id,
        habit_id,
        response.status_code,
        response.text,
    )
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

    logger.info(
        "edit_habit_api request, telegram_id=%s, habit_id=%s, param=%s",
        user.telegram_id,
        habit_id,
        param,
    )
    logger.debug(
        "edit_habit_api payload, telegram_id=%s, habit_id=%s, param=%s, value=%r",
        user.telegram_id,
        habit_id,
        param,
        value,
    )

    response: Response = patch(
        f"{API_URL}/api/habits/{habit_id}", headers=headers, json=data
    )
    logger.debug(
        "edit_habit_api response, telegram_id=%s, habit_id=%s, status=%s",
        user.telegram_id,
        habit_id,
        response.status_code,
    )

    if response.status_code == 204:
        logger.info(
            "edit_habit_api success, telegram_id=%s, habit_id=%s, param=%s",
            user.telegram_id,
            habit_id,
            param,
        )
        return True
    elif response.status_code == 401:
        logger.warning(
            "edit_habit_api unauthorized (401), telegram_id=%s, habit_id=%s",
            user.telegram_id,
            habit_id,
        )
        raise ExpiredTokenError(user=user)

    logger.error(
        "edit_habit_api failed, telegram_id=%s, habit_id=%s, param=%s, status=%s, error_message=%r",
        user.telegram_id,
        habit_id,
        param,
        response.status_code,
        response.text,
    )
    return None
