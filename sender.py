from aiogram import Bot
import inspect
import os
from time import sleep

from datetime import datetime

from core import core_log as log
# from handlers.common import get_registered_users_id
from users import reg_users

from handlers.common import split_text

from core.db_pool import db
# from core.db import db
# from core.db_ssh import db


# async def get_admins_id() -> list:
#     """
#     Получить список telegram_id администраторов бота для рассылки
#     :return: list
#     """
#     return [5107502329, 414366402]


async def send_bot_is_alive(bot: Bot) -> None:
    """
    Рассылка уведомлений админам о работе бота
    :param bot: Bot
    :return:
    """
    try:
        # for tg_user in await get_admins_id():
        for tg_user in await reg_users.get(admins=True):
            await bot.send_message(chat_id=tg_user, text=f'Время {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}. Бот работает.')
    except Exception as err:
        # if str(err) == 'Telegram server says - Forbidden: bot was blocked by the user':
        #     await reg_users.deactivate(tg_user)
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
        # await db.connect()
        rows = await db.fetch(query=query)
        # await db.disconnect()

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

        # text_answer = 'Тестируем блокировку бота'
        # print(await reg_users.get())

        # если есть изменения
        if text_answer:
            # рассылка каждому подписчику
            # for tg_user in await get_registered_users_id():

            count_subscribers = 0

            for tg_user in await reg_users.get():
            # Рассылка только админам. Оставить только в t_bot, т.к. остальных зарегистрированных пользователей t_bot может не знать
            # for tg_user in await reg_users.get(admins=True):

                # if tg_user == 5107502329:

                count_subscribers += 1
                # Отправка по 100 пользователей
                if count_subscribers == 100:
                    # Пауза 3 секунды
                    sleep(3)
                    count_subscribers = 0

                try:
                    # если текст есть и он больше 4096 символов, то его надо резать на разные сообщения
                    if len(text_answer) > 4096:
                        for part_text in await split_text(text=text_answer):
                            # передаём порцию текста
                            await bot.send_message(chat_id=tg_user, text=part_text)
                    # если текст есть, но он меньше 4096 символов, то его можно передать одним сообщением
                    else:
                        # for tg_user in await get_admins_id():
                        await bot.send_message(chat_id=tg_user, text=text_answer)
                except Exception as err:
                    # Если пользователь заблокировал бота, деактивируем его
                    if str(err) == 'Telegram server says - Forbidden: bot was blocked by the user':
                        await reg_users.deactivate(tg_user)
                        await log.log(text=f'{str(tg_user)} {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
                                      facility=os.path.basename(__file__))

            return True
        return False

    except Exception as err:
        await log.log(text=f'[no chat_id] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
                      facility=os.path.basename(__file__))


