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

from handlers import common
from handlers import maintenance
from handlers import user_selections
from handlers import unknown

from core import core_log as log

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

async def get_broadcast_list() -> list:
    """
    Получить список telegram_id для рассылки
    :return: list
    """
    return [5107502329]


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
    @aiocron.crontab("30 * * * *")
    async def notifications():
        for tg_user in await get_broadcast_list():
            await bot.send_message(chat_id=tg_user, text=f'Время {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}. Бот работает.')
        print(datetime.now())

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
    # точка входа
    asyncio.run(main())

