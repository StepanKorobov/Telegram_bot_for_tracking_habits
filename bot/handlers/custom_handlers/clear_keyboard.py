import logging

from loader import bot
from telebot.types import CallbackQuery

logger = logging.getLogger(__name__)


@bot.callback_query_handler(func=lambda call: call.data == "clear_keyboard")
def clear_keyboard(call: CallbackQuery) -> None:
    """
    Очистка меню - полностью убирает inline клавиатуру

    Args:
        call: Данные с кнопки inline.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.from_user.id
    message_id: int = call.message.message_id

    logger.info(
        "callback clear_keyboard, user_id=%s, chat_id=%s",
        user_id,
        chat_id,
    )
    logger.debug(
        "callback data=%r, user_id=%s, chat_id=%s, message_id=%r",
        call.data,
        user_id,
        chat_id,
        message_id,
    )

    try:
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None,
        )
        bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
        bot.answer_callback_query(
            callback_query_id=call.id,
            text="Клавиатура убрана!",
        )
        bot.delete_state(
            user_id=user_id,
            chat_id=chat_id,
        )

        logger.info(
            "clear_keyboard finished successfully, user_id=%s, chat_id=%s, message_id=%s",
            user_id,
            chat_id,
            message_id,
        )

    except Exception as exc:
        logger.exception(
            "error while clearing keyboard, user_id=%s, chat_id=%s, message_id=%s, exc=%r",
            user_id,
            chat_id,
            message_id,
            exc,
        )
