from telebot.handler_backends import State, StatesGroup


class HabitState(StatesGroup):
    name = State()
    description = State()
    goal = State()
    terms = State()
