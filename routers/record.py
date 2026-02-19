from record.week.week import get_this_week_num
from keyboards.callback import *
from states.record_states import RecordStates
from services.postgre_db import get_section, get_section_data, add_record_data, get_record_data, add_get_section_data_return_id

from aiogram import Router, types, F
from aiogram.filters import Command
import logging
from aiogram.fsm.context import FSMContext

router = Router()

places = {
    "1": "онлайн",#онлайн
    "2": "Ломо", #Ломо
    "3": "Вяземский",#Вяземский
    "4": "Другие",#Другие
}

# Начало
@router.message(Command("record"))
async def cmd_book(message: types.Message, state: FSMContext):
    await state.clear()  # Сбрасываем любое предыдущее состояние
    record_data = await get_record_data(int(message.from_user.id))
    await state.update_data(record_data = record_data)
    if len(record_data) <= 4:
        await state.set_state(RecordStates.PLACE)
        await message.answer(
            "🏢 Выберите место проведения:",
            reply_markup=place_kb
        )
    else:
        await message.answer(
                "Сначала отпишитесь от секций.\n"
                "Максимум можно записаться на 4 одновременно.\n\n"
                f"Вы записаны на {len(record_data)} из 4. Отписаться /unsubscribe")

@router.callback_query(lambda c: c.data == 'Назад', RecordStates.PLACE)
async def back_to_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text("Запись отменена. Для начала новой записи нажмите /record")

# Обработчики кнопок "Назад"
@router.callback_query(lambda c: c.data == 'Назад', RecordStates.DAY)
async def back_to_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(RecordStates.PLACE)
    await callback_query.message.edit_text("🏢 Выберите место проведения:", reply_markup=place_kb)

# Обработчики callback'ов для выбора места
@router.callback_query(lambda c: c.data in ['1', '2', '3', '4'], RecordStates.PLACE)
# Обработчики кнопок "Назад"
@router.callback_query(lambda c: c.data == 'Назад', RecordStates.TIME)
async def process_place(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data != 'Назад':
        place_name = places[callback_query.data]
        await state.update_data(place=callback_query.data, place_name=place_name)
    else:
        data = await state.get_data()
        place_name = data['place_name']
    await state.set_state(RecordStates.DAY)
    
    await callback_query.message.edit_text(f"📍 Место: {place_name}\n\n📅 Выберите день недели:", reply_markup=day_kb)




# Обработчики callback'ов для выбора дня
@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6'], RecordStates.DAY)
# Обработчики кнопок "Назад"
@router.callback_query(lambda c: c.data == 'Назад', RecordStates.WEEK)
async def process_day(callback_query: types.CallbackQuery, state: FSMContext):
    day_map = {
        '1': 'Понедельник',
        '2': 'Вторник',
        '3': 'Среда',
        '4': 'Четверг', 
        '5': 'Пятница',
        '6': 'Суббота'
    }
    if callback_query.data != 'Назад':
        day_name = day_map[callback_query.data]
        await state.update_data(day=callback_query.data, day_name=day_name)
    
    await state.set_state(RecordStates.TIME)
    
    data = await state.get_data()
    
    await callback_query.message.edit_text(
        f"📍 Место: {data['place_name']}\n"
        f"📅 День: {data['day_name']}\n\n"
        f"🕒 Выберите время:", reply_markup=time_kb)


# Обработчики кнопок "Назад"
@router.callback_query(lambda c: c.data == 'Назад', RecordStates.TEACHER_SECTION)
# Обработчики callback'ов для выбора дня
@router.callback_query(lambda c: c.data in ['1', '2', '3', '4', '5', '6', '7', '8'], RecordStates.TIME)
async def process_timr(callback_query: types.CallbackQuery, state: FSMContext):
    time_map = {
        '1': '8-9',
        '2': '9-11',
        '3': '11-13',
        '4': '13-15', 
        '5': '15-17',
        '6': '17-19',
        '7': '19-21',
        '8': '21-23'
        }
    if callback_query.data != 'Назад':
        await state.update_data(time_name=time_map[callback_query.data], time=int(callback_query.data))
    await state.set_state(RecordStates.WEEK)

    week = {1: "чётная", 0: "нечётная"}
    await callback_query.message.edit_text(
        f"🏢 Выберите недели для записи:\n"
        f"Сейчас: {week[get_this_week_num()]}", reply_markup=week_kb)

# Назад к выбору секций
@router.callback_query(lambda c: c.data == 'Назад', RecordStates.CONFIRMATION)
# Обработчики callback'ов для выбора времени
@router.callback_query(lambda c: c.data in ['0', '1', '2'], RecordStates.WEEK)
async def process_section(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data != 'Назад':
        await state.update_data(week=callback_query.data)
    await state.set_state(RecordStates.TEACHER_SECTION)
    
    data = await state.get_data()
    data_section = await get_section_data(data['day'], data['time'], data['place'])
    await state.update_data(data_section=data_section)
    section = []
    for i in data_section:
        section.append(f"{i['section']} - {i['coach']}")
        
    #section = ["Жёсткая ебля - Платонова"]
    week = {'1': "чётная", '0': "нечётная", '2': "каждая"}
    await callback_query.message.edit_text(
        f"📋 Подтвердите запись:\n\n"
        f"📍 Место: {data['place_name']}\n"
        f"📅 День: {data['day_name']}\n"
        f"🕒 Время: {data['time_name']}\n"
        f"🕒 Недели: {week[data['week']]}\n\n"
        f"Выберите секцию\n", reply_markup=make_kb_list(section, "Не нашли нужную секцию?") )


# Подтвержедие
@router.callback_query(lambda c: c.data not in set(['Назад', 'Не нашли нужную секцию?']), RecordStates.TEACHER_SECTION)
async def confirm(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    if callback_query.data != 'Назад':
        num = int(callback_query.data)
        await state.update_data(num=num)
    else:
        num = data['num']
    await state.set_state(RecordStates.CONFIRMATION)
    data = await state.get_data()
    
    data_section = data['data_section']
    section = []
    for i in data_section:
        section.append(f"{i['section']} - {i['coach']}")
        
    week = {'1': "чётная", '0': "нечётная", '2': "каждая"}
    await callback_query.message.edit_text(
        f"📋 Подтвердите запись:\n\n"
        f"📍 Место: {data['place_name']}\n"
        f"📅 День: {data['day_name']}\n"
        f"🕒 Время: {data['time_name']}\n"
        f"🕒 Недели: {week[data['week']]}\n"
        f"🏠 Секция: {section[num]}\n\n"
        f"Всё верно?\n", reply_markup=confirm_kb)

# Запись в бд
@router.callback_query(lambda c: c.data == 'Подтвердить', RecordStates.CONFIRMATION)
async def confirm(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    section_id = data['data_section'][data['num']]['id']
    if section_id not in [i['section_id'] for i in data['record_data']]:
        await add_record_data(callback_query.from_user.id, section_id, data['week'])
        await callback_query.message.edit_text(
            f"Вы записались на\n\n"
            f"{data['data_section'][data['num']]['section']} - {data['data_section'][data['num']]['coach']}")
    else:
        await callback_query.message.edit_text("Вы уже были записаны на эту секцию")
    
# Выбор секции и преподавателя
@router.callback_query(lambda c: c.data == 'Не нашли нужную секцию?', RecordStates.TEACHER_SECTION)
async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    week = {'1': "чётная", '0': "нечётная", '2': "каждая"}
    await callback_query.message.edit_text(
        f"📍 Место: {data['place_name']}\n"
        f"📅 День: {data['day_name']}\n"
        f"🕒 Время: {data['time_name']}\n"
        f"🕒 Недели: {week[data['week']]}\n\n"
        "Введите ФИО преподавателя:")
    await state.set_state(RecordStates.COACH)

@router.message(RecordStates.COACH)
async def process_confirmation(message: types.Message, state: FSMContext):
    coach = message.text.strip()
    await state.update_data(coach=coach)
    await message.answer("Введите название секции")
    await state.set_state(RecordStates.SECTION)

@router.message(RecordStates.SECTION)
async def process_confirmation(message: types.Message, state: FSMContext):
    section = message.text.strip()
    data = await state.get_data()
    
    data_section = await get_section(section, data['coach'], data['day'], data['time'], data['place'])
    if data_section == []:
        data_section = await add_get_section_data_return_id(section, data['coach'], data['day'], data['time'], data['place'])
    section_id = data_section[0]['id']
    if section_id not in [i['section_id'] for i in data['record_data']]:
        if await add_record_data(message.from_user.id, section_id, data['week']):
            await message.answer("Готово!")
        else:
            await message.answer("Ошибка внесения записи в бд :( ")
    else:
        await message.answer("Вы уже были записаны на эту секцию")
    await state.clear()
    
