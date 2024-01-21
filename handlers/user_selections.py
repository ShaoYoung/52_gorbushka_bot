from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from states.user_state import UserState
from keyboards.keyboards import get_reply_keyboard
from keyboards.keyboards import get_inline_keyboard
from keyboards.keyboards import UserChoiceCallbackFactory
from datetime import datetime
from handlers.common import main_menu


router = Router()


# State - None
@router.callback_query(StateFilter(None))
async def callbacks_without_state(callback: CallbackQuery):
    """
    Обработчик нажатия Inline Buttons пользователем без статуса
    :param callback: callback
    :return:None
    """
    await callback.answer(text='Наберите команду /start')


# State - choosing_choosing_category
@router.callback_query(UserState.choosing_category, UserChoiceCallbackFactory.filter(F.action == 'category'))
async def callbacks_choosing_category(callback: CallbackQuery, callback_data: UserChoiceCallbackFactory, state: FSMContext):
    """
    Обработчик нажатия Inline Button (выбор категории). Текущий статус пользователя = choosing_category
    :param callback: callback
    :param callback_data: callback_data
    :param state: Текущий статус пользователя
    :return: None
    """
    category = callback_data.choice
    print(f'Категория - {category}')
    # записываем выбранную категорию в хранилище FSM
    await state.update_data(chosen_category=category)

    # TODO Запрос в БД. Поиск вендоров по выбранной категории

    buttons = {
        'HONOR, HUAWEI': {
            'action': 'vendor',
            'choice': 'HONOR, HUAWEI'
        },
        'SAMSUNG': {
            'action': 'vendor',
            'choice': 'SAMSUNG'
        },
    }

    # TODO Добавить эмодзи
    buttons.update({'Назад': {
        'action': 'back',
        'choice': category}, })
    keyboard = get_inline_keyboard(buttons, [1])
    await callback.message.answer(text=f'Категория {category}\nВыберите вендор:', reply_markup=keyboard)

    # Устанавливаем пользователю состояние 'choosing_vendor'
    await state.set_state(UserState.choosing_vendor)

    # удаляем клавиатуру после нажатия
    await callback.message.edit_reply_markup()
    # await callback.answer()


# State - choosing_vendor, action - back
@router.callback_query(UserState.choosing_vendor, UserChoiceCallbackFactory.filter(F.action == 'back'))
async def callbacks_choosing_vendor_back(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия Inline Button (выбор категории). Текущий статус пользователя = choosing_vendor, action - back
    :param callback: callback
    :param state: Текущий статус пользователя
    :return: None
    """
    # category = callback_data.choice
    # print(f'Была выбрана категория - {category}')
    # Устанавливаем пользователю состояние 'choosing_category'
    await state.set_state(UserState.choosing_category)
    # удаляем клавиатуру после нажатия
    await callback.message.edit_reply_markup()
    # заново вызываем обработчик
    await main_menu(callback.message, state)


# State - choosing_vendor
@router.callback_query(UserState.choosing_vendor, UserChoiceCallbackFactory.filter(F.action == 'vendor'))
async def callbacks_choosing_vendor(callback: CallbackQuery, callback_data: UserChoiceCallbackFactory, state: FSMContext):
    """
    Обработчик нажатия Inline Button (выбор вендора). Текущий статус пользователя = choosing_vendor
    :param callback: callback
    :param callback_data: callback_data
    :param state: Текущий статус пользователя
    :return: None
    """
    user_data = await state.get_data()
    category = user_data['chosen_category']

    vendor = callback_data.choice
    print(f'Категория - {category}. Вендор - {vendor}')
    # записываем выбранный вендор в хранилище FSM
    # await state.update_data(chosen_vendor=vendor)

    # TODO Добавить эмодзи
    buttons = {'Назад': {
        'action': 'back',
        'choice': category}, }

    keyboard = get_inline_keyboard(buttons, [1])

    # TODO Запрос в БД. Поиск товаров по категории и вендору по выбранной категории

    await callback.message.answer(text=f'Категория {category}\nВендор {vendor}\nТовары скоро появятся', reply_markup=keyboard)

    # Устанавливаем пользователю состояние 'studying_products'
    await state.set_state(UserState.studying_products)

    # очистка State
    # await state.clear()

    # удаляем клавиатуру после нажатия
    await callback.message.edit_reply_markup()
    # await callback.answer()


# State - studying_products, action - back
@router.callback_query(UserState.studying_products, UserChoiceCallbackFactory.filter(F.action == 'back'))
async def callbacks_studying_products_back(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия Inline Button (выбор категории). Текущий статус пользователя = choosing_vendor, action - back
    :param callback: callback
    :param state: Текущий статус пользователя
    :return: None
    """
    user_data = await state.get_data()
    category = user_data['chosen_category']

    # Устанавливаем пользователю состояние 'choosing_category'
    await state.set_state(UserState.choosing_category)

    # очистка State
    # await state.clear()

    # удаляем клавиатуру после нажатия
    await callback.message.edit_reply_markup()
    # заново вызываем обработчик
    await callbacks_choosing_category(callback, UserChoiceCallbackFactory(action='category', choice=category), state)

