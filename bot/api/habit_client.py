from datetime import datetime

from bot.database.database import User
from config_data.config import API_URL
from requests import delete, get, patch, post, put
from requests.models import Response

from api.authentication import ExpiredTokenError, refresh_token, refresh_token_decorator


@refresh_token_decorator
def add_habit_api(user: User, habit_data: dict[str, str | datetime]) -> bool:
    """
    Функция добавления нового пользователя в API

    :param user: Пользователь
    :type user: User
    :param habit_data: Словарь с привычкой
    :type habit_data: Dict
    :return: True or False
    :rtype: bool
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
    Функция получения всех привычек пользователя из API

    :param user: Пользователь
    :type user: User
    :return: Список словарей привычек
    :rtype: list[dict[str, str | int]] | None
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
    Функция удаления одной привычки пользователя через API

    :param user: Пользователь
    :type user: User
    :param habit_id: ID привычки для удаления
    :type habit_id: int
    :return: True or False
    :rtype: bool | None
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
    Функция удаления всех привычек пользователя через API

    :param user: Пользователь
    :type user: User
    :return: True or False
    :rtype: bool | None
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
    Функция полного редактирования привычки через API

    :param user: Пользователь
    :type user: User
    :param habit_id: ID привычки для удаления
    :type habit_id: int
    :param habit_data: Обновлённые данные о привычке
    :type habit_data: dict[str, str]
    :return: True or False
    :rtype: bool | None
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
    Функция Частичного редактирования привычки через API

    :param user: Пользователь
    :type user: User
    :param habit_id: ID привычки для удаления
    :type habit_id: int
    :param param: Параметр значение которого будет обновлено
    :type param: str
    :param value: Значение параметра
    :type value: str | int
    :return: True or False
    :rtype: bool | None
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
