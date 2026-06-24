from telebot.handler_backends import State, StatesGroup


class ReminderState(StatesGroup):
    reminder = State()
    hour_change = State()
    minute_change = State()
