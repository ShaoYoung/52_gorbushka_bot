import asyncio
import logging

# В документации по aiogram используется config_reader, а не dotenv
from config_reader import config

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from handlers import common
from handlers import choice_currency

# bot
# bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)


async def main(maintenance_mode: bool = False):
    # включаем логирование
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a",
                        format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")


    # Deploy на pythonanywhere
    # https://docs.aiogram.dev/en/dev-3.x/api/session/aiohttp.html
    # from aiogram.client.session.aiohttp import AiohttpSession
    #
    # session = AiohttpSession(proxy="protocol://host:port/")
    # bot = Bot(token="bot_token", session=session)

    # bot
    # для импорта bot в обработчиках его можно сделать глобальным
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)

    # Диспетчер
    # В реальной жизни значение maintenance_mode будет взято из стороннего источника (например, конфиг или через API)
    # bool тип является иммутабельным, его смена в рантайме ни на что не повлияет
    # dp = Dispatcher(maintenance_mode=True)
    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    dp = Dispatcher(maintenance_mode=maintenance_mode, storage=MemoryStorage())

    # подключаем обработчики
    dp.include_router(common.router)
    dp.include_router(choice_currency.router)

    # Удаляем все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Поллинг новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    # точка входа
    asyncio.run(main())

