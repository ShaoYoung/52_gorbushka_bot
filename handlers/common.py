from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.types import FSInputFile, URLInputFile

import os
import json

from states.user_state import UserState
from keyboards.keyboards import get_reply_keyboard
from keyboards.keyboards import get_inline_keyboard
from calculation import calculation
# from bot import bot

router = Router()

# имя файла в пользователями
bot_users_file = 'bot_users.json'
# список id пользователей (глобальный, хранится в памяти во время работы бота)
registered_users_id = list()


async def set_registered_users_id() -> None:
    """
    Заполнение списка registered_users_id из файла
    :return: None
    """
    global registered_users_id
    if os.path.exists(bot_users_file):
        with open(bot_users_file, 'r') as json_file:
            registered_users = json.load(json_file)
            registered_users_id.clear()
            for user in registered_users:
                registered_users_id.append(user.get('id'))


async def add_new_user(user: dict) -> bool:
    """
    Регистрация нового пользователя бота. Добавляет пользователя в файл, добавляет id пользователя в список
    :param user: пользователь (словарь{id, full_name})
    :return: bool
    """
    global registered_users_id
    registered_users_id.append(user.get('id'))
    if os.path.exists(bot_users_file):
        with open(bot_users_file, 'r') as json_file:
            registered_users = json.load(json_file)
        with open(bot_users_file, 'w') as json_file:
            registered_users.append(user)
            json.dump(registered_users, json_file)
    else:
        with open(bot_users_file, 'w') as json_file:
            json.dump([user], json_file)
    return True


async def main_menu(message: Message, state: FSMContext):
    """
    Основное меню
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    keyboard = get_reply_keyboard(['Возврат в основное меню'], [1])
    await message.answer(text='Я знаю курсы валют.', reply_markup=keyboard)

    # Получаем валюты из словаря er-api.
    buttons = {}
    for key in calculation.get_all_exchange_rates_erapi()['exchange_rates'].keys():
        buttons.update({key: {
            'action': 'choice',
            'currency': key
        }})
    keyboard = get_inline_keyboard(buttons, [6])
    await message.answer(text='Выберите первую валюту:', reply_markup=keyboard)
    # Устанавливаем пользователю состояние 'choosing_first_currency'
    await state.set_state(UserState.choosing_first_currency)


@router.message(StateFilter(None), Command(commands=['start', 'Start', 'старт', 'Старт']))
async def cmd_start(message: Message, state: FSMContext):
    """
    Команда 'Start'. State не установлен.
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    global registered_users_id
    if not registered_users_id:
        await set_registered_users_id()

    # print(registered_users_id)
    if message.chat.id in registered_users_id:
        await message.answer(text='Я вас знаю, вы уже зарегистрированы.\nПродолжайте работать.')
    else:
        if await add_new_user({'id': message.chat.id, 'full_name': message.from_user.full_name}):
            await message.answer(text='Вы у меня первый раз.\nЯ вас зарегистрировал, можете работать.')
        else:
            await message.answer(text='Вы у меня первый раз.\nЗарегистрировать вас у меня не получилось.')
    await main_menu(message, state)


@router.message(F.text == 'Возврат в основное меню')
async def return_in_main_menu(message: Message, state: FSMContext):
    """
    Возврат в основное меню
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    # очистка State
    await state.clear()
    await main_menu(message, state)


@router.message(F.text == 'Возврат к выбору первой валюты')
async def return_to_choice_first_currency(message: Message, state: FSMContext):
    """
    Возврат к выбору первой валюты (фактически дубль 'Возврата в основное меню', сделано просто для примера)
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    # очистка State
    await state.clear()
    await main_menu(message, state)


@router.message(Command(commands='log'))
async def cmd_log(message: Message):
    """
    Отправка файла с логами в чат пользователю
    :param message:
    :return:
    """
    await message.answer(text='Файл с логами:')
    file_from_pc = FSInputFile('log.log')
    await message.answer_document(file_from_pc)


@router.message(Command(commands='get_bot_users'))
async def cmd_get_bot_users(message: Message):
    """
    Получить пользователей бота
    :param message:
    :return:
    """
    if os.path.exists(bot_users_file):
        with open(bot_users_file, 'r') as json_file:
            registered_users = json.load(json_file)
        text_answer = ''
        for user in registered_users:
            text_answer += str(user).replace('{', '').replace('}', '') + '\n'
        await message.answer(text=f'Пользователи бота:\n{text_answer}')
    else:
        await message.answer(text='У бота пока нет пользователей.')


@router.message(F.text.startswith(''))
async def cmd_incorrectly(message: Message):
    """
    Обработчик всех неизвестных команд (если ни один из обработчиков этого роутера не сработал и пришёл текст
    :param message: текстовое сообщение
    :return: None
    """
    await message.reply(f'Я не знаю команду <b>"{message.text}"</b>')
    await message.answer('Пожалуйста, попробуйте ещё раз.')


@router.message(F.animation)
@router.message(F.photo)
@router.message(F.sticker)
@router.message(F.contact)
async def unknown_message(message: Message):
    """
    Обработчик неизвестных сообщений
    :param message: сообщение типа (из списка выше)
    :return: None
    """
    await message.reply(f'Я не знаю <b> что с этим делать </b>')




