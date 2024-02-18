from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core import core_log as log

import os
import inspect

router = Router()


# Можно добавить фильтры
# @router.message(F.animation)
# @router.message(F.photo)
# @router.message(F.sticker)
# @router.message(F.contact)
# Обработка любого сообщения
@router.message()
async def unknown_message(message: Message, state: FSMContext):
    """
    Обработчик неизвестных сообщений
    :param message: любое сообщение, не попавшее ни в один обработчик
    :param state: текущий статус
    :return: None
    """
    try:
        # очистка State
        await state.clear()
        await message.reply(f'Я не знаю <b> что с этим делать </b>')
    except Exception as err:
        await log.log(text=f'[{str(message.chat.id)}] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error', facility=os.path.basename(__file__))
        await message.answer(text='Не понял последнюю команду.\nПовторите, пожалуйста.')
