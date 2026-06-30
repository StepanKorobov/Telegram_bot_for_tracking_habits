from telebot.handler_backends import State, StatesGroup


class HabitState(StatesGroup):
    """Состояния для добавления привычки."""

    name = State()
    description = State()
    goal = State()
    terms = State()
