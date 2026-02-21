from api.habit_client import get_habit_api
from bot.database.database import User
from loader import bot
from telebot.types import Message
from utils.misc.displaying_habit import displaying_habit
from utils.user_decorator import check_user_registration, with_current_user


@bot.message_handler(commands=["habit"])
@with_current_user
def get_habit(message: Message, current_user: User):
    """Команда получения списка всех привычек"""

    habits: str | None = get_habit_api(user=current_user)
    if habits:
        habits: str = displaying_habit(habits)
        bot.send_message(message.from_user.id, habits)
    else:
        bot.send_message(message.from_user.id, "У Вас пока ещё нет привычек")
