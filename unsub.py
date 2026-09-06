from record.week.week import get_this_week_num
from keyboards.callback import *
from states.unsub_states import UnsubStates
from services.postgre_db import del_all_user_record, del_user_record, get_record_section_data

from aiogram import Router, types, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

# Начало
@router.message(Command("unsub"))
async def cmd_unsub(message: types.Message, state: FSMContext):
    await state.clear()  # Сбрасываем любое предыдущее состояние
    await state.set_state(UnsubStates.unsub)
    await message.answer("Отписаться от",reply_markup=unsub_kb)

@router.callback_query(lambda c: c.data == 'Назад', UnsubStates.del_all)
@router.callback_query(lambda c: c.data == 'Назад', UnsubStates.select)
async def cmd_unsub_back(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()  # Сбрасываем любое предыдущее состояние
    await state.set_state(UnsubStates.unsub) 
    await callback_query.message.edit_text("Отписаться от",reply_markup=unsub_kb)

@router.callback_query(lambda c: c.data == 'Назад', UnsubStates.conf_del)
@router.callback_query(lambda c: c.data == 'секции', UnsubStates.unsub)
async def select_section(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UnsubStates.select)
    if callback_query.data != 'Назад':
        records = await get_record_section_data(int(callback_query.from_user.id))
        await state.update_data(records=records)
    else:
        data = await state.get_data()
        records = data['records']
    ls = [f"{i['section']}, {i['name_day']}, {i['name_time']}" for i in records]
    await callback_query.message.edit_text('Секцию, чтобы отписаться',reply_markup=make_kb_list(ls, 'Выйти'))
    

@router.callback_query(lambda c: c.data not in set(['Назад', 'Выйти']), UnsubStates.select)
async def select_conf_del(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UnsubStates.conf_del)
    num = int(callback_query.data)
    await state.update_data(num=num)
    data = await state.get_data()
    record = data['records'][num]
    await callback_query.message.edit_text(f"Подтвердите удаление:\n\n{record['section']}\n{record['name_day']}\n{record['name_time']}",reply_markup=confirm_kb)  

@router.callback_query(lambda c: c.data == 'Выйти', UnsubStates.select)
async def exit(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text(f"Вы вышли из отписок от секции")
    
@router.callback_query(lambda c: c.data == 'Подтвердить', UnsubStates.conf_del)
async def select_del(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    record = data['records'][data['num']]
    section_id = record['section_id']
    if await del_user_record(int(callback_query.from_user.id), section_id):
        await callback_query.message.edit_text(f"Вы отписались от секции\n{record['section']}")
    else:
        await callback_query.message.edit_text("Ошибка")
    
@router.callback_query(lambda c: c.data == 'всех секций', UnsubStates.unsub)
async def conf_dell_all(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UnsubStates.del_all)
    await callback_query.message.edit_text("Подвердите отписку от всех секций",reply_markup=confirm_kb)

@router.callback_query(lambda c: c.data == 'Подтвердить', UnsubStates.del_all)
async def dell_all(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    if await del_all_user_record(int(callback_query.from_user.id)):
        await callback_query.message.edit_text("Вы отписались от всех секций")
    else:
        await callback_query.message.edit_text("Ошибка")
    
