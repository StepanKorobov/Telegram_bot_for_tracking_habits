from loader import bot
from telebot.types import CallbackQuery


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

    bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=None,
    )
    bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )
    bot.answer_callback_query(callback_query_id=call.id, text="Клавиатура убрана!")
    bot.delete_state(
        user_id=user_id,
        chat_id=chat_id,
    )
