from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    """
    Статус пользователя
    """
    choosing_category = State()
    choosing_vendor = State()
    studying_products = State()
