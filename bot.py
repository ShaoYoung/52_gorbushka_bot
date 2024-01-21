import asyncio
import logging

# В документации по aiogram используется config_reader, а не dotenv
from config_reader import config

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from handlers import common
from handlers import maintenance
from handlers import user_selections

# bot
# bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)


async def main(maintenance_mode: bool = False):
    """
    Основная
    :param maintenance_mode: режим обслуживания
    :return: None
    """
    # включаем логирование
    # TODO Логирование переделать
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a",
                        format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")

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

