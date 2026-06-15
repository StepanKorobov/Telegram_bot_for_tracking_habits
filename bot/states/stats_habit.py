from telebot.handler_backends import State, StatesGroup


class StatsState(StatesGroup):
    stats = State()
    stats_one_habit = State()
