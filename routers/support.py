from states.support_states import SupStates, SupStates
from filters.filters import IsAdmin, IsSupportMessage
from keyboards.callback import *
from services.postgre_db import get_id_add_ticket, add_ticket_msg, get_user_ticket, get_ticket_msg, update_status_ticket, update_feedback_score_ticket, update_feedback_ticket

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext 

router = Router()

# Обработчик команды /support
@router.message(F.text == "/support")
async def start_support_message(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(SupStates.sup)
    tickets = await get_user_ticket(message.from_user.id)
    await state.update_data(tickets=tickets)
    if len(tickets) >= 3:
        await message.answer("У вас уже 3 активных обращения, дождитесь их решения.", reply_markup=small_sup_kb)
    else:
        await message.answer("Поддержка", reply_markup=support_kb)

### ОБРАЩЕНИЕ
# Начали создавать обращение
@router.callback_query(lambda c: c.data == 'Назад', SupStates.create_confirm)
@router.callback_query(lambda c: c.data == 'Назад', SupStates.watch_ticket)
@router.callback_query(lambda c: c.data == 'Обращения')
async def tickets(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupStates.ticket)
    data = await state.get_data()
    tickets = data['tickets']
    ls_ticket = [i['topic'] for i in tickets]
    await callback_query.message.edit_text("Обращения", reply_markup=make_kb_list(ls_ticket, "Выйти"))

## Новое сообщение
@router.callback_query(lambda c: c.data not in set(['Назад', 'Выйти']), SupStates.ticket)
async def watch_ticket(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupStates.watch_ticket)
    data = await state.get_data()
    num = int(callback_query.data)
    await state.update_data(num=num)
    ticket = data['tickets'][num] 
    status = {  1: '🆕 Отправлено', 2: '🔄 В работе', 4: '📝 Возобновлено'}
    ans = await get_ticket_msg(ticket['ticket_id'])
    text = (''.join([f"\n{'Ответ' if i['is_from_admin'] else 'Сообщение'}:\n{i['msg']}" for i in ans]))[:3000]
    await callback_query.message.edit_text(f"Статус: {status[ticket['status_id']]}\nТекст:\n\n{ticket['topic']}{text}", reply_markup=ticket_kb)

@router.callback_query(lambda c: c.data == 'Новое сообщение', SupStates.watch_ticket)
async def msg(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupStates.msg)
    await callback_query.message.edit_text('Напишите ОДНО сообщение с описанием проблемы или вопроса для поддержки.')

@router.message(SupStates.msg)
async def conf_msg(message: types.Message, state: FSMContext):
    msg = message.text
    await state.update_data(msg=msg)
    await state.set_state(SupStates.action_confirm)
    await message.answer(f'Ваше сообщение: {msg}', reply_markup=confirm_kb)

@router.callback_query(lambda c: c.data == 'Подтвердить', SupStates.action_confirm)
async def send_msg(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not(await add_ticket_msg(data['tickets'][data['num']]['ticket_id'], data['msg'], False)):
        await callback_query.message.edit_text("Ошибка. Напишите на почту ars.rys.ry@gmail.com")
    else:
        await callback_query.message.edit_text('Вы отправили сообщение')
    
@router.callback_query(lambda c: c.data == 'Выйти', SupStates.ticket)
async def exit(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text('Можете спокойно использовать команды.\n/help')

# Вернуться к /support
@router.callback_query(lambda c: c.data == 'Назад', SupStates.ticket)
@router.callback_query(lambda c: c.data == 'Назад', SupStates.topic)
async def back_to_start_support_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupStates.sup)
    await callback_query.message.edit_text("Поддержка", reply_markup=support_kb)

## Закрыть обращкние
@router.callback_query(lambda c: c.data == 'Закрыть обращение', SupStates.watch_ticket)
async def close_ticket(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupStates.feedback)
    data = await state.get_data()
    if await update_status_ticket(data['tickets'][data['num']]['ticket_id'], 3):
        await callback_query.message.edit_text('Обращение закрыто', reply_markup=feedback_kb)
    else:
        await callback_query.message.edit_text('Произошла ошибка')
        
@router.callback_query(lambda c: c.data == 'Оценить поддержку', SupStates.feedback)
async def feedback_ticket(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupStates.score)
    await callback_query.message.edit_text('Поставьте оценку', reply_markup=score_kb)

@router.callback_query(SupStates.score)
async def score_ticket(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupStates.comment)
    data = await state.get_data()
    if await update_feedback_score_ticket(data['tickets'][data['num']]['ticket_id'], callback_query.data):
        await callback_query.message.edit_text(f'Оценка: {callback_query.data}\nХотите оставить отзыв? Просто напишите его следующим сообщением')
    else:
        await callback_query.message.edit_text('Произошла ошибка')
        
@router.message(SupStates.comment)
async def comment_ticket(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if await update_feedback_ticket(data['tickets'][data['num']]['ticket_id'], message.text):
        await message.answer('Спасибо за отзыв!')
    else:
        await message.answer('Произошла ошибка')
    await state.clear()
        

### СОЗДАТЬ ОБРАЩЕНИЕ
# Начали создавать обращение
@router.callback_query(lambda c: c.data == 'Создать обращение')
async def start_create_ticket(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupStates.topic)
    await callback_query.message.edit_text("Напишите кратко тему обращения.\nОграничение 64 символа.", reply_markup=back_kb)

#Вернулись к созданию обращения
@router.callback_query(lambda c: c.data == 'Назад', SupStates.create_confirm)
async def start_create_ticket(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupStates.topic)
    await callback_query.message.answer("Напишите кратко тему обращения.\nОграничение 64 символа.", reply_markup=back_kb)

# Обработчик сообщения в состоянии ожидания темы вопроса
@router.message(SupStates.topic)
async def process_topic(message: types.Message, state: FSMContext):
    if len(message.text) <= 64:
        await state.update_data(topic=message.text, user_id=message.from_user.id)
        await state.set_state(SupStates.question)
        await message.answer("Напишите ОДНО сообщение с описанием проблемы или вопроса для поддержки.")
    else:
        await message.answer("Напишите тему снова.\nСообщение больше 64 сиволов.")
        
# Обработчик сообщения в состоянии ожидания вопроса
@router.message(SupStates.question)
async def process_question(message: types.Message, state: FSMContext):
    await state.update_data(msg=message.text)
    await state.set_state(SupStates.create_confirm)
    data = await state.get_data()
    await message.answer(f"Подтвердите отпрвку\n\n{data['topic']}\n\n{data['msg']}", reply_markup=confirm_kb)

# Записываем сообщение в бд
@router.callback_query(lambda c: c.data == 'Подтвердить', SupStates.create_confirm)
async def process_record(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ans = await get_id_add_ticket(data['user_id'], data['topic'])
    if ans == [] or not(await add_ticket_msg(ans[0]['ticket_id'], data['msg'], False)):
        await callback_query.message.edit_text("Ошибка. Напишите на почту ars.rys.ry@gmail.com")
    else:
        await callback_query.message.edit_text("Ваш вопрос отправлен. Мы ответим как только сможем.")
    await state.clear()

"""

# Обработчик ответов администраторов
@router.message(IsAdmin(), IsSupportMessage())
async def admin_reply(message: types.Message):
    original_message = message.reply_to_message.text
    user_id = int(original_message.split("ID: ")[1].split(")")[0])
    
    await bot.send_message(
        user_id,
        f"Ответ поддержки:\n\n{message.text}"
    )
    
    await message.answer("Ваш ответ отправлен.")

# Обработчик inline кнопки "Ответить"
@router.callback_query(F.data.startswith("reply_"))
async def process_reply_button(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[1])
    await state.update_data(target_user_id=user_id)
    await state.set_state(SupportStates.response)
    await callback.message.answer(f"Введите ответ для пользователя {user_id}:")
    await callback.answer()

# Обработчик ответа администратора в состоянии ожидания
@router.message(SupportStates.response)
async def process_admin_response(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['target_user_id']
    
    await bot.send_message(
        user_id,
        f"Ответ от поддержки:\n\n{message.text}"
    )
    
    await message.answer("Ваш ответ был отправлен пользователю.")
    await state.clear()

"""
