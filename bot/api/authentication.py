from typing import Dict

from requests import post
from requests.models import Response

from config_data.config import API_URL


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

    json_data: Dict[str: str | int] = {
        "telegram_id": telegram_id,
        "username": username,
        "password": password,
    }
    response: Response = post(f"{API_URL}/api/auth/login", json=json_data)
    if response.status_code == 200:
        return True
    else:
        return False


def get_token(username: str, password: str) -> Dict[str, str] | None:
    """
    Функция для получения токена из API по логину и паролю

    :param username: Имя пользователя в телеграмме
    :type username: str
    :param password: Пароль пользователя
    :type password: str
    :return: Словарь с токенами | Ничего
    :rtype: Dict[str, str] | None
    """

    from_data: Dict[str: str | int] = {
        "username": username,
        "password": password,
    }
    response: Response = post(f"{API_URL}/api/auth/token", data=from_data)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def refresh_token(token: str):
    json_data: Dict[str: str] = {
        "refresh_token": token,
    }
    response = post(f"{API_URL}/api/auth/refresh_token", json=json_data)
    return response.json()
