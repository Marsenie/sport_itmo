from states.del_states import DelStates
from services.postgre_db import del_user_data

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Router, types
from aiogram.types import Message

router = Router()


# Обработчик команды /del
@router.message(Command('del'))
async def cmd_reg(message: types.Message, state: FSMContext):
    await message.answer("Напишите УДАЛИТЬ для удаления.")
    await state.set_state(DelStates.waiting_phrase)


@router.message(DelStates.waiting_phrase)
async def process_email(message: types.Message, state: FSMContext):
    phrase = message.text.strip()
    await state.clear()
    if phrase.lower() == "удалить":
        if await del_user_data(message.from_user.id):
            return await message.answer("Ваши данные удалены")
        else:
            return await message.answer("Произошла ошибка удаления данных")
    await message.answer("Отменено")
