from states.sup_admin_states import SupAdmStates
from filters.filters import IsAdmin
from keyboards.callback import *
from services.postgre_db import get_user_ticket, get_ticket_msg, update_status_ticket, update_tickets_issue_admin, add_ticket_msg, get_admin_tickets
from alerts.alerts import send_answer_suport

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext 

router = Router()

# Обработчик команды /support
@router.message(F.text == "/ans", IsAdmin())
async def start_support_message(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(SupAdmStates.sup)
    await message.answer("Действия.", reply_markup=sub_adm_kb)
    
@router.callback_query(lambda c: c.data == 'Назад', SupAdmStates.get)
async def callback_start_support_message(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupAdmStates.sup)
    await callback_query.message.edit_text("Действия.", reply_markup=sub_adm_kb)
    
### Получить тикеты
@router.callback_query(lambda c: c.data == 'Получить тикеты', SupAdmStates.sup)
async def tickets(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupAdmStates.get_tickets)
    if await update_tickets_issue_admin(callback_query.from_user.id):
        await callback_query.message.edit_text("Вы взяли тикеты!", reply_markup=sub_adm_get_kb)
    else:
        await callback_query.message.edit_text("Ошибка")

### Ответ на тикеты
# Активные
@router.callback_query(lambda c: c.data == 'Активные тикеты', SupAdmStates.sup)
@router.callback_query(lambda c: c.data == 'Активные тикеты', SupAdmStates.get_tickets)
@router.callback_query(lambda c: c.data == 'Назад', SupAdmStates.choice)
@router.callback_query(SupAdmStates.close)
async def get_tickets(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupAdmStates.get)
    tickets = await get_admin_tickets(callback_query.from_user.id)
    await state.update_data(tickets = tickets)
    ls_ticket = [i['topic'] for i in tickets]
    await callback_query.message.edit_text("Тикеты", reply_markup=make_kb_list(ls_ticket, "Выйти"))

@router.callback_query(lambda c: c.data == 'Выйти', SupAdmStates.get)
@router.callback_query(lambda c: c.data == 'Выйти', SupAdmStates.choice)
async def exit_tickets(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text("вы вышли. /help")

# Тикет
@router.callback_query(lambda c: c.data not in ['Назад', 'Выйти'], SupAdmStates.get)
@router.callback_query(lambda c: c.data == 'Назад', SupAdmStates.confirm)
async def ticket(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupAdmStates.choice)
    data = await state.get_data()
    if callback_query.data != 'Назад':
        num = int(callback_query.data)
        await state.update_data(num = num)
    else:
        num = data['num']
    ticket = data['tickets'][num] 
    status = {2: '🔄 В работе', 4: '📝 Возобновлено'}
    ans = await get_ticket_msg(ticket['ticket_id'])
    text = (''.join([f"\n{'Ответ' if i['is_from_admin'] else 'Сообщение'}:\n{i['msg']}" for i in ans]))[:3000]
    await state.update_data(text = text)
    await callback_query.message.edit_text(f"Статус: {status[ticket['status_id']]}\nuser_id:\n{ticket['user_id']}\nТекст:\n\n{ticket['topic']}{text}", reply_markup=ticket_kb)

# Новое сообщение
@router.callback_query(lambda c: c.data == 'Новое сообщение', SupAdmStates.choice)
@router.callback_query(lambda c: c.data == 'Назад', SupAdmStates.confirm_msg)
async def msg(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupAdmStates.msg)
    await callback_query.message.edit_text('Напишите ответ')

@router.message(SupAdmStates.msg)
async def conf_msg(message: types.Message, state: FSMContext):
    msg = message.text
    await state.update_data(msg=msg)
    await state.set_state(SupAdmStates.confirm_msg)
    await message.answer(f'Ваше сообщение: {msg}', reply_markup=confirm_kb)

@router.callback_query(lambda c: c.data == 'Подтвердить', SupAdmStates.confirm_msg)
async def send_msg(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(SupAdmStates.close)
    text = data['text'] + "\nОтвет:\n" + data['msg']
    ticket = data['tickets'][data['num']]
    await send_answer_suport(ticket['user_id'], text)
    if not(await add_ticket_msg(ticket['ticket_id'], data['msg'], True)):
        await callback_query.message.edit_text("Ошибка. Напишите на почту ars.rys.ry@gmail.com")
    else:
        await update_status_ticket(ticket['ticket_id'], 3)
        await callback_query.message.edit_text('Вы отправили сообщение')

# Закрыть
@router.callback_query(lambda c: c.data == 'Закрыть обращение', SupAdmStates.choice)
async def confirm(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupAdmStates.confirm)
    await callback_query.message.edit_text(f'Закрыть обращение', reply_markup=confirm_kb)

@router.callback_query(lambda c: c.data == 'Подтвердить', SupAdmStates.confirm)
async def tickets(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupAdmStates.close)
    data = await state.get_data()
    if await update_status_ticket(data['tickets'][data['num']]['ticket_id'], 3):
        await callback_query.message.edit_text('Обращение закрыто')
        ticket = data['tickets'][data['num']]
        await send_answer_suport(ticket['user_id'], 'Ваше jбращение закрыто')
    else:
        await callback_query.message.edit_text('Произошла ошибка')
    
