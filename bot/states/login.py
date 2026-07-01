from telebot.handler_backends import State, StatesGroup


class LoginState(StatesGroup):
    """Состояния для регистрации и входа в бота."""

    registration = State()
    login = State()
