from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from states.user_state import UserState
from keyboards.keyboards import get_reply_keyboard
from keyboards.keyboards import get_inline_keyboard
from keyboards.keyboards import CurrencyCallbackFactory
from calculation import calculation
from datetime import datetime


router = Router()


# State - None
@router.callback_query(StateFilter(None))
async def callbacks_without_state(callback: CallbackQuery):
    """
    Обработчик нажатия Inline Buttons пользователем без статуса
    :param callback: callback
    :return:None
    """
    await callback.answer(text='Вернитесь в основное меню')


# State - choosing_first_currency, CurrencyCallbackFactory.filter - просто для проверки фабрики колбэков
@router.callback_query(UserState.choosing_first_currency, CurrencyCallbackFactory.filter(F.action == 'choice'))
async def callbacks_first_currency_chosen(callback: CallbackQuery, callback_data: CurrencyCallbackFactory, state: FSMContext):
    """
    Обработчик нажатия Inline Button (выбор первой валюты). Текущий статус пользователя = choosing_first_currency
    :param callback: callback
    :param callback_data: callback_data
    :param state: Текущий статус пользователя
    :return: None
    """
    # print(f'Первая валюта - {callback_data.currency}')
    # записываем данные в хранилище FSM
    await state.update_data(chosen_currency=callback_data.currency)

    keyboard = get_reply_keyboard(['Возврат в основное меню', 'Возврат к выбору первой валюты'], [2])
    await callback.message.answer(text=f'Первая валюта <b>{callback_data.currency}</b>', reply_markup=keyboard)

    # # Пока валюты получаем из словаря. Может быть потом будет список.
    # buttons = {}
    # for key, value in calculation.get_currencies().items():
    #     buttons.update({f'{key} - {value}': {
    #         'action': 'choice',
    #         'currency': key
    #     }})

    # Получаем валюты из словаря er-api.
    buttons = {}
    for key in calculation.get_all_exchange_rates_erapi()['exchange_rates'].keys():
        buttons.update({key: {
            'action': 'choice',
            'currency': key
        }})
    keyboard = get_inline_keyboard(buttons, [6])
    await callback.message.answer(text=f'Выберите вторую валюту:', reply_markup=keyboard)

    # Устанавливаем пользователю состояние 'choosing_second_currency'
    await state.set_state(UserState.choosing_second_currency)

    await callback.answer()


# State - choosing_first_currency, CurrencyCallbackFactory.filter - просто для проверки фабрики колбэков
@router.callback_query(UserState.choosing_second_currency, CurrencyCallbackFactory.filter(F.action == 'choice'))
async def callbacks_second_currency_chosen(callback: CallbackQuery, callback_data: CurrencyCallbackFactory, state: FSMContext):
    """
    Обработчик нажатия Inline Button (выбор второй валюты). Текущий статус пользователя = choosing_second_currency
    :param callback: callback
    :param callback_data: callback_data
    :param state: Текущий статус пользователя
    :return: None
    """
    currency_data = await state.get_data()
    first_currency = currency_data['chosen_currency']
    # print(f'{first_currency = }')
    second_currency = callback_data.currency
    # print(f'{second_currency = }')

    if first_currency == second_currency:
        course = 1
    else:

        keyboard = get_reply_keyboard(['Возврат в основное меню'], [1])
        await callback.message.answer(text=calculation.get_course(first_currency, second_currency), reply_markup=keyboard)
    # очистка State
    await state.clear()

    await callback.answer()


