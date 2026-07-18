import logging

from config_data.config import DEFAULT_COMMANDS
from loader import bot
from telebot.types import Message

logger = logging.getLogger(__name__)


@bot.message_handler(commands=["help"])
def bot_help(message: Message) -> None:
    """
    Выводит список доступных команд с описанием.

    Args:
        message: Сообщение с данными.

    Returns:
        None.
    """

    logger.info(
        "command /help, user_id=%s",
        message.from_user.id,
    )

    text: list = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    logger.debug(
        "command help, user_id=%s, commands=%r",
        message.from_user.id,
        text,
    )

    bot.reply_to(message, "\n".join(text))
