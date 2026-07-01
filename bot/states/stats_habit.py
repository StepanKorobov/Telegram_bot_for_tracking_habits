from telebot.handler_backends import State, StatesGroup


class StatsState(StatesGroup):
    """Состояния для статистики по привычкам."""

    stats = State()
    stats_one_habit = State()
