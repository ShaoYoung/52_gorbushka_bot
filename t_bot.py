#!/usr/bin/python3

import asyncio
import logging
import inspect
import os

# В документации по aiogram используется config_reader, а не dotenv
from config import config

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from datetime import datetime

import aiocron
# import daemon

from handlers import common
from handlers import maintenance
from handlers import user_selections
from handlers import unknown

from users import reg_users
# from handlers.common import set_registered_users_id

from core import core_log as log

from sender import send_bot_is_alive
from sender import send_product_events

from utils import save_products

from core.db_pool import db
# from core.db import db
# from core.db_ssh import db

# bot
# bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)

from aiogram.exceptions import TelegramBadRequest


# Пример удаления всех сообщений, через цикл (aiogram 3.x)
# Можно запустить через @aiocron.crontab("0 * * * *")
# @router.message(Command("clear"))
# async def cmd_clear(message: Message, bot: Bot) -> None:
#     try:
#         # Все сообщения, начиная с текущего и до первого (message_id = 0)
#         for i in range(message.message_id, 0, -1):
#             await bot.delete_message(message.from_user.id, i)
#     except TelegramBadRequest as ex:
#         # Если сообщение не найдено (уже удалено или не существует),
#         # код ошибки будет "Bad Request: message to delete not found"
#         if ex.message == "Bad Request: message to delete not found":
#             print("Все сообщения удалены")

# async def get_broadcast_list() -> list:
#     """
#     Получить список telegram_id для рассылки
#     :return: list
#     """
#     return [5107502329]


async def main(maintenance_mode: bool = False):
    """
    Основная
    :param maintenance_mode: режим обслуживания
    :return: None
    """
    # включаем логирование
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a",
                        format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")
    await log.init()
    # имя модуля
    facility_name = os.path.basename(__file__)
    # имя функции
    module_name = inspect.currentframe().f_code.co_name
    await log.log(text=f'[no chat_id] {module_name} bot started', severity='info', facility=facility_name)
    # формат записи лога
    # await log.log(text=f'[{str(chat_id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))

    # bot
    # для импорта bot в обработчиках его можно сделать глобальным
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)

    # Выполнение задачи в определенное время (с определенной периодичностью). Аналог планировщика cron.
    # pip install aiocron
    # Время можно удобно настроить на сайте: https://crontab.guru/
    # Импортируйте aiocron и добавьте cron-задачу для отправки рассылки:
    # m h d(month) m d(week)

    @aiocron.crontab("0 */8 * * *")
    # @aiocron.crontab("* * * * *")
    async def bot_is_alive():
        await send_bot_is_alive(bot=bot)
        # try:
        #     for tg_user in await get_broadcast_list():
        #         await bot.send_message(chat_id=tg_user, text=f'Время {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}. Бот работает.')
        # except Exception as err:
        #     await log.log(text=f'[no chat_id] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
        #                   facility=os.path.basename(__file__))

    # @aiocron.crontab("* * * * *")
    # @aiocron.crontab("0 */4 * * *")
    @aiocron.crontab("*/2 * * * *")
    async def product_events():
        if await send_product_events(bot=bot):
            await save_products()

    # Закрытие pool каждые 5 минут. А надо ли?
    # @aiocron.crontab("*/5 * * * *")
    # async def db_disconnect():
    #     await db.disconnect()

    # загружаем список зарегистрированных действующих пользователей в список
    # await set_registered_users_id()
    await reg_users.set()
    # print(reg_users.users_id)
    # print(reg_users.admins_id)

    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    dp = Dispatcher(maintenance_mode=maintenance_mode, storage=MemoryStorage())

    # подключаем обработчики
    dp.include_router(maintenance.router)
    dp.include_router(common.router)
    dp.include_router(user_selections.router)
    dp.include_router(unknown.router)

    # Удаляем все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Поллинг новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    # with daemon.DaemonContext():
    # точка входа
    asyncio.run(main())

