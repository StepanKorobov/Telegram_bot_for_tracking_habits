from telebot.handler_backends import State, StatesGroup


class TrackState(StatesGroup):
    track = State()
    confirmation = State()
