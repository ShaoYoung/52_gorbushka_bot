from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    """
    Статус пользователя
    """
    choosing_first_currency = State()
    choosing_second_currency = State()
