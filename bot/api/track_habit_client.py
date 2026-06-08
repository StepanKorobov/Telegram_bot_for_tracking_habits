from typing import Dict

from bot.database.database import User
from bot.database.models import update_user_tokens
from config_data.config import API_URL
from requests import get, post, delete, patch, put
from requests.models import Response

from api.authentication import refresh_token


def track_habit_check_api(user: User, habit_id: int):
    token: str = user.to_json().get("api_token")
    headers: Dict[str:str] = {
        "Authorization": f"Bearer {token}",
    }
    data: Dict[str, int] = {
        "habit_id": habit_id,
    }

    response: Response = post(f"{API_URL}/api/habits_tracing/check", headers=headers, json=data)
    if response.status_code == 200:
        return True

    return False
