from aiogram import Bot
import inspect
import os

from datetime import datetime

from core import core_log as log
from handlers.common import get_registered_users_id
from handlers.common import split_text

# from core.db_pool import db
from core.db import db
# from core.db_ssh import db


async def get_admins_id() -> list:
    """
    Получить список telegram_id администраторов бота для рассылки
    :return: list
    """
    return [5107502329, 414366402]


async def send_bot_is_alive(bot: Bot) -> None:
    """
    Рассылка уведомлений админам о работе бота
    :param bot: Bot
    :return:
    """
    try:
        for tg_user in await get_admins_id():
            await bot.send_message(chat_id=tg_user, text=f'Время {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}. Бот работает.')
    except Exception as err:
        await log.log(text=f'[no chat_id] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
                      facility=os.path.basename(__file__))


async def send_product_events(bot: Bot) -> bool:
    """
    Рассылка уведомлений об изменении в продуктах
    :param bot:
    :return:
    """
    try:
        # интервал (timestamp от текущего времени), за который будут получены изменения в таблице history
        interval = '2 minute'
        # interval = '10 hour'
        # query = f"""SELECT h.event, h.price, w.category, w.vendor, w.description, w.price
        query = f"""SELECT h.event, w.description, w.price
                   FROM history h
                   LEFT JOIN warehouse w
                   ON h.product_id = w.product_id
                   WHERE h.dt > now() - interval '{interval}'
                   AND w.description <> '190'
                   ORDER BY h."event" """
        # print(query)
        await db.connect()
        rows = await db.fetch(query=query)
        await db.disconnect()

        text_answer = ''
        # event
        event_dict = {
            'entrance': ['<b><u>Появился:</u></b>'],
            'new': ['<b><u>Новый товар:</u></b>'],
            'over': ['<b><u>Закончился:</u></b>'],
            'price': ['<b><u>Новая цена:</u></b>'],
            'rewrite': ['<b><u>Изменилось описание:</u></b>']
        }

        for row in rows:
            if row[0] == 'entrance':
                event_dict.get(row[0]).append(f'{row[1]}, {row[2]}')
            elif row[0] == 'new':
                event_dict.get(row[0]).append(f'{row[1]}, {row[2]}')
            elif row[0] == 'over':
                event_dict.get(row[0]).append(f'{row[1]}')
            # не рассылать изменения цены
            # elif row[0] == 'price':
            #     event_dict.get(row[0]).append(f'{row[1]}, {row[2]}')
            elif row[0] == 'rewrite':
                event_dict.get(row[0]).append(f'{row[1]}')

        for value in event_dict.values():
            if len(value) > 1:
                text_answer += '\n'.join(value) + '\n'

        # если есть изменения
        if text_answer:
            # рассылка каждому подписчику
            for tg_user in await get_registered_users_id():
                # рассылка только админам
                # if tg_user == 414366402 or tg_user == 5107502329:

                # TODO оставить только в t_bot, т.к. остальных зарегистрированных пользователей t_bot не знает
                # if tg_user == 5107502329:

                # если текст есть и он больше 4096 символов, то его надо резать на разные сообщения
                if len(text_answer) > 4096:
                    for part_text in await split_text(text=text_answer):
                        # передаём порцию текста
                        await bot.send_message(chat_id=tg_user, text=part_text)
                # если текст есть, но он меньше 4096 символов, то его можно передать одним сообщением
                else:
                    # for tg_user in await get_admins_id():
                    await bot.send_message(chat_id=tg_user, text=text_answer)
            return True
        return False

        # interval = '4 hour'
        # # interval = '1 minute'
        # query = f"SELECT vendor, description, event FROM history where dt > now() - interval '{interval}'"
        #
        # # print(query)
        # product_events = ''
        # # text_answer = ''
        # await db.connect()
        # rows = await db.fetch(query=query)
        # await db.disconnect()
        # for count, row in enumerate(rows, start=1):
        #     product_events += f'<b><u>{count}.</u></b> {row[0]}, {row[1]}, {row[2]}\n'
        #     # text_answer += f'<b><u>{count}.</u></b> {row[0]}, {row[1]}, {row[2]}\n'
        #
        # text_answer = f'За прошедший(е) {interval} произошли следующие изменения:\n{product_events}' if len(product_events) else f'За прошедший(е) {interval} изменений не было'
        #

    except Exception as err:
        await log.log(text=f'[no chat_id] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
                      facility=os.path.basename(__file__))


