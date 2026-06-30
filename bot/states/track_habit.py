from telebot.handler_backends import State, StatesGroup


class TrackState(StatesGroup):
    """Состояния для отслеживания привычки."""

    track = State()
    confirmation = State()
