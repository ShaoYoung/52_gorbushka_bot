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

# from core import core_pg_ssh as pg
# from core import core_pg as pg
# from core import core_asyncpg as pg

from core.db import db
# from core.db_ssh import db

from config import macro
from core import core_log as log

import os
import json
import inspect

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
    Заполнение списка registered_users_id (из файла / из БД)
    :return: None
    """
    try:
        global registered_users_id

        # # из файла
        # if os.path.exists(bot_users_file):
        #     with open(bot_users_file, 'r') as json_file:
        #         registered_users = json.load(json_file)
        #         registered_users_id.clear()
        #         for user in registered_users:
        #             registered_users_id.append(user.get('id'))

        # из таблицы users БД
        registered_users_id.clear()
        query = 'select tg_id from users where active = TRUE'
        for tg_id in await db.fetch(query=query):
            registered_users_id.append(tg_id)
        print(registered_users_id)
    except Exception as err:
        await log.log(text=f'[no chat_id] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
                      facility=os.path.basename(__file__))


async def add_new_user(user: dict) -> bool:
    """
    Регистрация нового пользователя бота. Добавляет пользователя в файл / БД, добавляет id пользователя в список
    :param user: пользователь (словарь{id, full_name})
    :return: bool
    """
    try:
        global registered_users_id
        # добавляем id пользователя в список
        registered_users_id.append(user.get('id'))

        # # дописываем пользователя в файл
        # if os.path.exists(bot_users_file):
        #     with open(bot_users_file, 'r') as json_file:
        #         registered_users = json.load(json_file)
        #     with open(bot_users_file, 'w') as json_file:
        #         registered_users.append(user)
        #         json.dump(registered_users, json_file)
        # else:
        #     with open(bot_users_file, 'w') as json_file:
        #         json.dump([user], json_file)

        # ищем пользователя в таблице users по telegram_id
        query = f"SELECT active from users where tg_id = {user.get('id')}"
        rows = await db.fetch(query=query)
        # print(rows)
        # если пользователь есть, то возвращаем ему активность
        if rows:
            query = f"UPDATE users SET active = True WHERE tg_id = {user.get('id')}"
        # иначе записываем нового пользователя в таблицу users БД
        else:
            query = f"INSERT INTO users (name, tg_id, active) VALUES ('{user.get('full_name')}', {user.get('id')}, True)"
        # print(query)
        await db.execute(query=query)
        return True

    except Exception as err:
        await log.log(text=f'[no chat_id] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
                      facility=os.path.basename(__file__))


async def get_course_cbrf(currency: str = 'USD') -> float:
    """
    Курс ЦБ РФ
    :param currency: валюта
    :return: курс валюты к рублю
    """
    try:
        valute = f"./Valute[CharCode='{currency}']/Value"
        url = 'https://www.cbr.ru/scripts/XML_daily.asp'
        rate = float(ET.fromstring(requests.get(url=url).text).find(valute).text.replace(',', '.'))
        return rate
    except Exception as err:
        await log.log(text=f'[no chat_id] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
                      facility=os.path.basename(__file__))


async def set_exchange_rates() -> None:
    """
    Актуализируем курсы
    :return: None
    """
    global exchange_rates
    rate = await get_course_cbrf()
    # print(rate)
    # если есть курс, то сдвигаем список влево
    if rate:
        # оставляем только 29 + 1 значений
        while len(exchange_rates.get('rates')) >= 30:
            exchange_rates.get('rates').pop(0)
        exchange_rates.get('rates').append(rate)
        exchange_rates['last_updated_datetime'] = datetime.utcnow()
        # print(exchange_rates)


async def split_text(text: str, max_part_length: int = 4096, marker_symbol: str = '\n') -> list:
    """
    Разбивает текст на части
    :param text: текст
    :param max_part_length: максимальная длина части текста (4096 для telegram)
    :param marker_symbol: сигнальный символ (перенос строки)
    :return: список частей текста
    """
    parts_list = []
    # Режем сообщение по part_length символов
    i = 0
    total = len(text)
    while i < total:
        # ищем ближайший marker_symbol (начало новой строки)
        buf_end = i + max_part_length
        if buf_end >= total:
            buf_end = total
        else:
            while buf_end > i and text[buf_end:buf_end + 1] != marker_symbol:
                buf_end -= 1
        # добавляем порцию текста в список
        # print(f'Длина порции - {len(text[i:buf_end])}')
        parts_list.append(text[i:buf_end])
        # начало следующей порции
        i = buf_end
    return parts_list


async def main_menu(message: Message, state: FSMContext):
    """
    Основное меню
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    try:
        # очистка State
        await state.clear()

        # keyboard = await get_reply_keyboard(['Выбор категории', 'Отписаться', 'USD/RUB', 'График USD/RUB'], [2])
        # 27.01.2024 пока заменил на 2 кнопки
        # 10.02.2024 пока заменил на 3 кнопки (добавил "Отписаться")
        keyboard = await get_reply_keyboard(['Выбор категории', 'USD/RUB', 'Отписаться'], [2])
        # Удаление клавы
        # keyboard = ReplyKeyboardRemove()
        await message.answer(text='Я могу вам предложить', reply_markup=keyboard)

        # Получаем категории из БД
        query = "select category, count(*) from warehouse "
        where = "where warehouse_id=40 and balance>0 "
        group = "group by category order by category"
        query += where + group
        # print(query)
        rows = await db.fetch(query=query)
        # rows = pg.execute(query)
        buttons = {}
        for row in rows:
            buttons.update({f'{row[0]} ({row[1]})': {
                'action': 'category',
                'choice': f'{row[0]}'
            }})
        keyboard = await get_inline_keyboard(buttons, [1])
        await message.answer(text='Выберите категорию:', reply_markup=keyboard)
        # Устанавливаем пользователю состояние 'choosing_category'
        await state.set_state(UserState.choosing_category)
    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


@router.message(Command(commands=['start']))
async def cmd_start(message: Message, state: FSMContext):
    """
    Команда 'Start'. State любой.
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    try:
        global registered_users_id
        # при первой команде /start заполняем список telegram-id пользователей
        # если заполняем список telegram-id пользователей не заполнен, то заполняем его
        if not registered_users_id:
            await set_registered_users_id()

        # если id пользователя не в списке, то регистрируем его
        if message.chat.id not in registered_users_id:
            if await add_new_user({'id': message.chat.id, 'full_name': message.from_user.full_name}):
                await message.answer(text='Я вас зарегистрировал, можете работать.')
            else:
                await message.answer(text='Зарегистрировать вас у меня не получилось.')
        # переход в основное меню
        await main_menu(message, state)
    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


@router.message(Command(commands=['alllist']))
async def cmd_alllist(message: Message, state: FSMContext):
    """
    Команда /alllist. Вывод всех продуктов в одном сообщении
    :param message: message
    :param state: текущий статус
    :return:
    """
    try:
        # очистка State
        await state.clear()

        order = list()
        order.append("SAMSUNG")
        order.append("APPLE")
        order.append("APPLE IPHONE")
        order.append("FLY")
        order.append("INFINIX")
        order.append("TECNO")
        order.append("HONOR, HUAWEI")
        order.append("OnePlus")
        order.append("GOOGLE PIXEL")
        order.append("REALME")
        order.append("DYSON")
        order.append("GO PRO")
        order.append("SONY PS")
        order.append("XIAOMI")
        order.append("XIAOMI POCO")
        order.append("XIAOMI MI-серия")
        order.append("XIAOMI REDMI")
        order.append("HOTWAV")
        order.append("DOOGEE")
        order.append("ULEFONE")
        order.append("OUKITEL")
        order.append("BLACKVIEW")
        order.append("ATOUCH")
        order.append("UMIIO")
        order.append("X-PRIME")
        order.append("NOKIA")
        order.append("JBL")
        order.append("PITAKA")
        order.append("УМНАЯ КОЛОНКА")

        # предупреждаем пользователя, что дело не быстрое
        await message.answer(text='⌛ собираю информацию, немного подождите ⌛')

        #
        # 1 Сначала берём список Категорий
        # 2 Для каждой категории список Вендоров
        # 3 Для каждого вендора список Товаров
        #
        text = ""
        #
        # query Vendor
        #
        queryV = "select distinct vendor from warehouse where warehouse_id=40 and balance>0 order by vendor"
        rowsV = await db.fetch(query=queryV)
        # rowsV    = pg.execute( queryV, conn=env['db']['conn'] )
        for rowV in rowsV:
            # если вендора ещё нет, то добавляем
            if rowV[0] not in order:
                order.append(rowV[0])

        for vendor in order:
            #
            # add Vendor in answers text
            #
            text += "\n------------------------------\n" + str(vendor) + "\n------------------------------"
            #
            # query Category
            #
            queryC = "select distinct category from warehouse where warehouse_id=40 and balance>0 and vendor = '" + str(
                vendor) + "' order by category"
            rowsC = await db.fetch(query=queryC)
            # rowsC    = pg.execute( queryC, conn=env['db']['conn'] )
            for rowC in rowsC:
                #
                # add Category in answers text
                #
                text += "\n" + str(rowC[0]) + "\n"

                #
                # query Products
                #
                queryP = "select description, price from warehouse where warehouse_id=40 and balance>0 and category = '" + str(
                    rowC[0]) + "' and vendor='" + str(vendor) + "' order by description"
                rowsP = await db.fetch(query=queryP)
                # rowsP   = pg.execute( queryP, conn=env['db']['conn'] )
                for rowP in rowsP:
                    text += f'{rowP[0]} - {rowP[1]}\n'
                    # text += "{0}  - {1}\n".format( rowP[0], rowP[1] )

        #
        # Macro replace
        #
        # Замена на символы
        for c in macro.keys():
            text = text.replace(c, macro[c])

        # print(f'Длина всего сообщения - {len(text)}')
        # если ничего не нашлось
        if not len(text):
            await message.answer(text='Пока ничего не нашёл.\nПопробуйте повторить запрос.')
        # если текст есть и он больше 4096 символов, то его надо резать на разные сообщения
        elif len(text) > 4096:
            for part_text in await split_text(text=text):
                # передаём порцию текста
                # print(f'Длина порции - {len(part_text)}')
                await message.answer(text=part_text)
        # если текст есть, но он меньше 4096 символов, то его можно передать одним сообщением
        else:
            await message.answer(text=text)

    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


@router.message(Command(commands=['about']))
async def cmd_about(message: Message, state: FSMContext):
    """
    Команда /about
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    try:
        # очистка State
        await state.clear()

        about_content = """Уважаемые коллеги, друзья!
    
        Мы рады приветствовать вас в нашем боте.
    
        Здесь вы можете ознакомиться с ассортиментом товаров и ценами.
        По любым интересующим вопросам обращайтесь по телефону 8 963 962 7770"""
        await message.answer(text=about_content)
    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


@router.message(F.text == 'Выбор категории')
async def return_in_main_menu(message: Message, state: FSMContext):
    """
    Возврат в основное меню
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    try:
        # очистка State
        await state.clear()
        await main_menu(message, state)
    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


@router.message(F.text == 'Отписаться')
async def unsubscribe(message: Message, state: FSMContext):
    """
    Отписаться
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    try:
        # очистка State
        await state.clear()

        global registered_users_id
        # если список telegram-id пользователей не заполнен, то заполняем его
        if not registered_users_id:
            await set_registered_users_id()

        if message.chat.id in registered_users_id:
            registered_users_id.remove(message.chat.id)
            # делаем пользователя неактивным в таблице users БД
            query = f"UPDATE users SET active = False WHERE tg_id = {message.chat.id}"
            # print(query)
            await db.execute(query=query)
            await message.answer(text='Вы успешно отписаны от бота')

    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


@router.message(F.text == 'USD/RUB')
async def get_course_usd_rub(message: Message, state: FSMContext):
    """
    Отписаться
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    try:
        # очистка State
        await state.clear()

        global exchange_rates
        if exchange_rates['last_updated_datetime'].date() < datetime.utcnow().date():
            # print('Имеющиеся курсы устарели')
            await set_exchange_rates()
        await message.answer(text=f'Курс USD = {exchange_rates.get("rates")[-1]}')
    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


@router.message(F.text == 'График USD/RUB')
async def get_chart_usd_rub(message: Message, state: FSMContext):
    try:
        # TODO Сделать график USR/RUB
        # очистка State
        await state.clear()

        await message.answer(text='График в работе')
    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


@router.message(Command(commands='get_log'))
async def cmd_log(message: Message, state: FSMContext):
    """
    Отправка файла с логами в чат пользователю
    :param message:
    :param state: текущий статус
    :return:
    """
    try:
        # очистка State
        await state.clear()

        await message.answer(text='Файл с логами:')
        file_from_pc = FSInputFile('server.log')
        await message.answer_document(file_from_pc)
    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


@router.message(Command(commands='get_bot_users'))
async def cmd_get_bot_users(message: Message, state: FSMContext):
    """
    Получить пользователей бота
    :param message:
    :param state: текущий статус
    :return:
    """
    try:
        # очистка State
        await state.clear()

        # # из файла
        # if os.path.exists(bot_users_file):
        #     with open(bot_users_file, 'r') as json_file:
        #         registered_users = json.load(json_file)
        #     text_answer = ''
        #     for count, user in enumerate(registered_users, start=1):
        #         text_answer += f'{count}. {user.get("full_name")}\n'
        #     await message.answer(text=f'Пользователи бота:\n{text_answer}')
        # else:
        #     await message.answer(text='У бота пока нет пользователей.')

        # из таблицы users БД
        # получаем full_name всех пользователей из таблицы users со статусом active = True
        query = 'select name from users where active = TRUE'
        text_answer = ''
        for count, user in enumerate(await db.fetch(query=query), start=1):
            text_answer += f'{count}. {user[0]}\n'
        text_answer = f'Пользователи бота:\n{text_answer}' if len(text_answer) else 'У бота пока нет пользователей.'
        await message.answer(text=text_answer)

    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


@router.message(Command(commands=['macro']))
async def cmd_macro(message: Message, state: FSMContext):
    """
    Команда /macro. Расшифровка символов.
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    try:
        # очистка State
        await state.clear()

        text = "<code>"
        for c in macro.keys():
            text += f''
            text += "{0:16} {1}\n".format(c, str(macro[c]))
        text += "</code>"
        # answer = dict()
        # answer.update( {"text":text} )
        await message.answer(text=text)
    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


@router.message(F.text.startswith(''))
async def cmd_incorrectly(message: Message, state: FSMContext):
    """
    Обработчик неизвестного текста (инициирует поиск в БД)
    :param message: текстовое сообщение
    :param state: текущий статус
    :return: None
    """
    try:
        # очистка State
        await state.clear()

        query_text = message.text
        query = "select description, price from warehouse "
        where = f"where warehouse_id=40 and (category ilike '%{query_text}%' or vendor ilike '%{query_text}%' or description ilike '%{query_text}%') and balance>0 "
        order = "order by description"
        query += where + order
        # print(query)

        rows = await db.fetch(query=query)

        if rows:
            text = f'Результат поиска: <b>"{query_text}"</b>:\n'
            for row in rows:
                text += f'{row[0]} - {row[1]}\n'
            # если текст больше 4096 символов, то его надо резать на разные сообщения
            if len(text) > 4096:
                for part_text in await split_text(text=text):
                    # передаём порцию текста
                    await message.answer(text=part_text)
            # если текст меньше 4096 символов, то его можно передать одним сообщением
            else:
                await message.answer(text=text)
        else:
            await message.answer(text=f'Поиск <b>"{query_text}"</b> не дал результатов')
    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Что-то пошло не так...\nПопробуйте ещё раз.')


