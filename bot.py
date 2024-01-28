import asyncio
import logging
import inspect
import os

# В документации по aiogram используется config_reader, а не dotenv
from config import config

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from handlers import common
from handlers import maintenance
from handlers import user_selections

from core import core_log as log

# bot
# bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)


async def main(maintenance_mode: bool = False):
    """
    Основная
    :param maintenance_mode: режим обслуживания
    :return: None
    """
    # включаем логирование
    # logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a",
    #                     format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")
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

    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    dp = Dispatcher(maintenance_mode=maintenance_mode, storage=MemoryStorage())

    # подключаем обработчики
    dp.include_router(maintenance.router)
    dp.include_router(common.router)
    dp.include_router(user_selections.router)

    # Удаляем все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Поллинг новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    # точка входа
    asyncio.run(main())

