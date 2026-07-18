import logging

from config_data.config import DEFAULT_COMMANDS
from telebot.types import BotCommand

logger = logging.getLogger(__name__)


def set_default_commands(bot) -> None:
    """Функция устанавливает команды и их описание"""

    logger.debug("Setting default commands %s", DEFAULT_COMMANDS)
    bot.set_my_commands([BotCommand(*i) for i in DEFAULT_COMMANDS])
