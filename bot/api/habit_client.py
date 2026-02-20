from requests import post, get
from requests.models import Response
from config_data.config import API_URL
from typing import Dict
from bot.database.database import User
from bot.database.models import update_user_tokens
from api.authentication import refresh_token


def add_habit_api(user: User, habit_data: Dict) -> bool:
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
    headers: Dict[str: str] = {
        "Authorization": f"Bearer {token}",
    }
    data: Dict[str: str] = {
        "habit_name": habit_data["name"],
        "description": habit_data["description"],
    }
    response: Response = post(f"{API_URL}/api/habits", headers=headers, json=data)
    if response.status_code == 201:
        return True
    elif response.status_code == 401:
        tokens = refresh_token(token=user.to_json().get("api_token_refresh"))
        update_user_tokens(telegram_id=user.telegram_id, token_data=tokens)
    else:
        return False


def get_habit_api(user: User) -> str | None:
    token: str = user.to_json().get("api_token")
    headers: Dict[str: str] = {
        "Authorization": f"Bearer {token}",
    }
    response: Response = get(f"{API_URL}/api/habits", headers=headers)
    result = response.json()["habits"]
    if result:
        habits_list = [i["habit_name"] for i in result]
        habits = "\n".join(habits_list)
        return habits
    return None
