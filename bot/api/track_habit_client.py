from bot.database.database import User
from bot.database.models import update_user_tokens
from config_data.config import API_URL
from requests import get, post, delete, patch, put
from requests.models import Response

from api.authentication import refresh_token, refresh_token_decorator, ExpiredTokenError


@refresh_token_decorator
def track_habit_check_api(user: User, habit_id: int) -> bool:
    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }
    data: dict[str, int] = {
        "habit_id": habit_id,
    }

    response: Response = post(f"{API_URL}/api/habits_tracing/check", headers=headers, json=data)

    if response.status_code == 200:
        return True
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return False


def track_habit_get_stats_all(user: User) -> list[dict[str, str]] | None:
    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }

    response: Response = get(f"{API_URL}/api/habits_tracking/statistic", headers=headers)

    if response.status_code == 200:
        return response.json()["result"]
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return None


def track_habit_get_stats(user: User, habit_id: int) -> list[dict[str, str]] | None:
    token: str = user.to_json().get("api_token")
    headers: dict[str, str] = {
        "Authorization": f"Bearer {token}",
    }

    response: Response = get(f"{API_URL}/api/habits_tracking/statistic/{habit_id}", headers=headers)

    if response.status_code == 200:
        return response.json()["result"]
    elif response.status_code == 401:
        raise ExpiredTokenError(user=user)

    return None
