import requests
import xml.etree.ElementTree as ET
from datetime import datetime

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
# from bot import bot

router = Router()

# имя файла с пользователями
bot_users_file = 'bot_users.json'
# список id пользователей (глобальный, хранится в памяти во время работы бота)
registered_users_id = list()
# Дата последнего обновления и курсы USD (для кэширования курсов во время работы бота, т.к. в API есть ограничения)
exchange_rates = {
    'last_updated_datetime': datetime.utcnow().replace(year=2023),
    'rates': list()
}


async def set_registered_users_id() -> None:
    """
    Заполнение списка registered_users_id (пока из файла, потом надо будет переделать на БД)
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
    # добавляем id пользователя в список
    registered_users_id.append(user.get('id'))
    # пока дописываем пользователя в файл, позже переделать на БД
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


async def get_course_cbrf(currency: str = 'USD') -> float:
    """
    Курс ЦБ РФ
    :param currency: валюта
    :return: курс валюты к рублю
    """
    valute = f"./Valute[CharCode='{currency}']/Value"
    url = 'https://www.cbr.ru/scripts/XML_daily.asp'
    rate = float(ET.fromstring(requests.get(url=url).text).find(valute).text.replace(',', '.'))
    return rate


async def set_exchange_rates() -> None:
    """
    Актуализируем курсы
    :return: None
    """
    global exchange_rates
    rate = await get_course_cbrf()
    # print(rate)
    while len(exchange_rates.get('rates')) >= 30:
        exchange_rates.get('rates').pop(0)
    exchange_rates.get('rates').append(rate)
    exchange_rates['last_updated_datetime'] = datetime.utcnow()
    # print(exchange_rates)


async def main_menu(message: Message, state: FSMContext):
    """
    Основное меню
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    keyboard = get_reply_keyboard(['Выбор категории', 'Отписаться', 'USD/RUB', 'График USD/RUB'], [2])
    await message.answer(text='Я могу вам предложить', reply_markup=keyboard)

    # Получаем категории из БД
    # TODO Запрос категорий из БД
    buttons = {
        'ТЕЛЕФОНЫ': {
            'action': 'category',
            'choice': 'ТЕЛЕФОНЫ'
        },
        'ТЕЛЕФОНЫ ПРОТИВОУДАРНЫЕ': {
            'action': 'category',
            'choice': 'ТЕЛЕФОНЫ ПРОТИВОУДАРНЫЕ'
        },
    }
    keyboard = get_inline_keyboard(buttons, [1])
    await message.answer(text='Выберите категорию:', reply_markup=keyboard)
    # Устанавливаем пользователю состояние 'choosing_category'
    await state.set_state(UserState.choosing_category)


@router.message(Command(commands=['start']))
async def cmd_start(message: Message, state: FSMContext):
    """
    Команда 'Start'. State не установлен.
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    global registered_users_id
    # при первой команде /start заполняем список telegram-id пользователей
    if not registered_users_id:
        await set_registered_users_id()

    # если id пользователя не в списке, то регистрируем его
    if message.chat.id not in registered_users_id:
        if await add_new_user({'id': message.chat.id, 'full_name': message.from_user.full_name}):
            await message.answer(text='Вы у меня первый раз.\nЯ вас зарегистрировал, можете работать.')
        else:
            await message.answer(text='Вы у меня первый раз.\nЗарегистрировать вас у меня не получилось.')
    # переход в основное меню
    await main_menu(message, state)


@router.message(F.text == 'Выбор категории')
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


@router.message(F.text == 'Отписаться')
async def unsubscribe(message: Message):
    """
    Отписаться
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    global registered_users_id
    if message.chat.id in registered_users_id:
        registered_users_id.remove(message.chat.id)
    # TODO Добавить функционал удаления id из БД
        await message.answer(text='Вы успешно отписаны от бота')


@router.message(F.text == 'USD/RUB')
async def get_course_usd_rub(message: Message):
    """
    Отписаться
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    global exchange_rates
    if exchange_rates['last_updated_datetime'].date() < datetime.utcnow().date():
        # print('Имеющиеся курсы устарели')
        await set_exchange_rates()
    await message.answer(text=f'Курс USD = {exchange_rates.get("rates")[-1]}')


@router.message(F.text == 'График USD/RUB')
async def get_chart_usd_rub(message: Message):
    await message.answer(text='График в работе')


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
    # TODO Переписать на поиск в БД
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




