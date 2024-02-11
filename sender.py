from aiogram import Bot
import inspect
import os

from datetime import datetime

from core import core_log as log
from handlers.common import get_registered_users_id

from core.db import db
# from core.db_ssh import db


async def get_admins_id() -> list:
    """
    Получить список telegram_id администраторов бота для рассылки
    :return: list
    """
    return [5107502329]


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


async def send_product_events(bot: Bot) -> None:
    """
    Рассылка уведомлений об изменении в продуктах
    :param bot:
    :return:
    """
    try:
        # интервал (timestamp от текущего времени), за который будут получены изменения в таблице history
        interval = '4 hour'
        # interval = '1 minute'
        query = f"SELECT vendor, description, event FROM history where dt > now() - interval '{interval}'"
        # print(query)
        product_events = ''
        for count, row in enumerate(await db.fetch(query=query), start=1):
            product_events += f'{count}. {row[0]}, {row[1]}, {row[2]}\n'
        text_answer = f'За прошедший {interval} произошли следующие изменения:\n{product_events}' if len(product_events) else f'За прошедший {interval} изменений не было'

        # print(await get_registered_users_id())
        # TODO рассылка каждому подписчику
        for tg_user in await get_registered_users_id():
            if tg_user == 414366402 or tg_user == 5107502329:
                # пока только админам
                # for tg_user in await get_admins_id():
                await bot.send_message(chat_id=tg_user, text=text_answer)

    except Exception as err:
        await log.log(text=f'[no chat_id] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
                      facility=os.path.basename(__file__))


