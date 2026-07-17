import logging

from telebot.custom_filters import StateFilter

import handlers  # noqa
from loader import bot
from utils.set_bot_commands import set_default_commands

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    logger.info("bot started")
    bot.polling()
    logger.info("bot stopped")
    # bot.infinity_polling()
