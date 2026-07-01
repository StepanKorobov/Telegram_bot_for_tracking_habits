from config_data.config import DEFAULT_COMMANDS
from loader import bot
from telebot.types import Message


@bot.message_handler(commands=["help"])
def bot_help(message: Message) -> None:
    """
    Выводит список доступных команд с описанием.

    Args:
        message: Сообщение с данными.

    Returns:
        None.
    """

    text: list = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, "\n".join(text))
