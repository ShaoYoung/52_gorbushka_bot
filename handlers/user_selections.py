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
from handlers.common import split_text

# from core import core_pg_ssh as pg
# from core import core_pg as pg
# from core import core_asyncpg as pg
# from core.db import db
from core.db_ssh import db
from core import core_log as log

import inspect
import os


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
    try:
        category = callback_data.choice
        # print(f'Категория - {category}')
        # записываем выбранную категорию в хранилище FSM
        await state.update_data(chosen_category=category)

        query = "select vendor, count(*) from warehouse "
        where = f"where warehouse_id=40 and category='{category}' and balance>0 "
        group = "group by vendor order by vendor"
        query += where + group
        # print(query)

        rows = await db.fetch(query=query)
        buttons = {}
        for row in rows:
            buttons.update({f'{row[0]} ({row[1]})': {
                'action': 'vendor',
                'choice': f'{row[0]}'
            }})

        # Кнопка "Назад"
        buttons.update({'⏪ Назад': {
            'action': 'back',
            'choice': category}, })
        keyboard = await get_inline_keyboard(buttons, [1])
        await callback.message.answer(text=f'Категория <b>"{category}"</b>\nВыберите вендор:', reply_markup=keyboard)

        # Устанавливаем пользователю состояние 'choosing_vendor'
        await state.set_state(UserState.choosing_vendor)

        # удаляем клавиатуру и сообщение после нажатия
        await callback.message.delete()

        # удаляем клавиатуру после нажатия
        # await callback.message.edit_reply_markup()
        # убираем "часики" на кнопке
        # await callback.answer()
    except Exception as err:
        await log.log(text=f'[{str(callback.message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await callback.message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


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

    # удаляем клавиатуру и сообщение после нажатия
    await callback.message.delete()

    # удаляем клавиатуру после нажатия
    # await callback.message.edit_reply_markup()
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
    try:
        user_data = await state.get_data()
        category = user_data['chosen_category']

        vendor = callback_data.choice
        # print(f'Категория - {category}. Вендор - {vendor}')
        # записываем выбранный вендор в хранилище FSM
        # await state.update_data(chosen_vendor=vendor)

        # Кнопка "Назад"
        buttons = {'⏪ Назад': {
            'action': 'back',
            'choice': category}, }
        keyboard = await get_inline_keyboard(buttons, [1])

        query = "select description, price from warehouse "
        where = f"where warehouse_id=40 and category='{category}' and vendor='{vendor}' and balance>0 "
        order = "order by description"
        query += where + order
        # print(query)

        rows = await db.fetch(query=query)
        if rows:
            text = f'Категория <b>"{category}"</b>\nВендор <b>"{vendor}"\n</b>'
            for row in rows:
                text += f'{row[0]} - {row[1]}\n\n'
            # если текст больше 4096 символов, то его надо резать на разные сообщения
            if len(text) > 4096:
                parts_text = await split_text(text=text)
                # выводим все сообщения, кроме последнего
                for i in range(len(parts_text) - 1):
                    await callback.message.answer(text=parts_text[i])
                # последнее сообщение с кнопкой "Назад"
                await callback.message.answer(text=parts_text[-1], reply_markup=keyboard)
            # если текст меньше 4096 символов, то его можно передать одним сообщением
            else:
                await callback.message.answer(text=text, reply_markup=keyboard)
        else:
            await callback.message.answer(text=f'<b>В категории "{category}",\nвендор "{vendor}"\nтовары пока отсутствуют</b>', reply_markup=keyboard)

        # Устанавливаем пользователю состояние 'studying_products'
        await state.set_state(UserState.studying_products)

        # очистка State
        # await state.clear()

        # удаляем клавиатуру и сообщение после нажатия
        await callback.message.delete()

        # удаляем клавиатуру после нажатия
        # await callback.message.edit_reply_markup()
        # await callback.answer()
    except Exception as err:
        await log.log(text=f'[{str(callback.message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await callback.message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


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

    # удаляем клавиатуру и сообщение после нажатия
    # await callback.message.delete()

    # удаляем клавиатуру после нажатия
    # await callback.message.edit_reply_markup()

    # заново вызываем обработчик
    await callbacks_choosing_category(callback, UserChoiceCallbackFactory(action='category', choice=category), state)

