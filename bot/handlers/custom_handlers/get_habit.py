import logging

from api.habit_client import get_habit_api
from bot.database.database import User
from loader import bot
from telebot.types import Message
from utils.misc.displaying_habit import displaying_habit
from utils.user_decorator import check_user_registration, with_current_user

logger = logging.getLogger(__name__)


@bot.message_handler(commands=["habit"])
@with_current_user
def get_habit(message: Message, current_user: User) -> None:
    """
    Команда получения списка всех привычек

    Args:
        message: Сообщение с данными
        current_user: текущий пользователь полученный из БД

    Returns:
        None
    """

    chat_id: int = message.chat.id
    user_id: int = message.from_user.id

    logger.info(
        "command: /hobit, user_id=%s, chat_id=%s",
        user_id,
        chat_id,
    )

    habits: str | None = get_habit_api(user=current_user)
    logger.debug(
        "raw habits response for user_id=%s, habits: %r",
        user_id,
        habits,
    )

    if habits:
        logger.info(
            "user %s (chat_id=%s) has habits",
            user_id,
            chat_id,
        )
        habits: str = displaying_habit(habits)
        logger.debug(
            "rendered habits for user_id=%s, length=%s, habits=%r",
            user_id,
            chat_id,
            habits,
        )
        bot.send_message(
            chat_id=chat_id,
            text=habits,
        )
    else:
        logger.info(
            "user %s (chat_id=%s) has no habits yet",
            user_id,
            chat_id,
        )
        bot.send_message(
            chat_id=chat_id,
            text="У Вас пока ещё нет привычек",
        )
