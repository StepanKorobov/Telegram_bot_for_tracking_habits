from telebot.handler_backends import State, StatesGroup


class EditState(StatesGroup):
    edit = State()
    option = State()
    name = State()
    description = State()
    goal = State()
    terms = State()
    remove = State()
