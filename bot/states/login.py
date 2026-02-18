from telebot.handler_backends import State, StatesGroup


class LoginState(StatesGroup):
    registration = State()
    login = State()
