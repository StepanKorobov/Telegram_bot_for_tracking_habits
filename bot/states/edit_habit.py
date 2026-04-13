from telebot.handler_backends import State, StatesGroup


class EditState(StatesGroup):
    edit = State()
    option = State()
    name = State()
    description = State()
    goal = State()
    terms = State()
    remove = State()
    name_desc_goal_only = State()
    description_only = State()
    goal_only = State()
    term_only = State()
