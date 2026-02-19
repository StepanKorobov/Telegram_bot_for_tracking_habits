from functools import wraps
from bot.database.database import Base, User, get_session
from bot.database.models import get_user_by_telegram_id


def with_current_user(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        current_user = get_user_by_telegram_id(telegram_id=message.from_user.id)
        # Можно ещё положить db
        return func(message, current_user=current_user, *args, **kwargs)

    return wrapper
