from states.supp_admin_states import SupAdmStates
from filters.filters import IsAdmin
from keyboards.callback import *
from services.postgre_db import get_user_ticket, get_ticket_msg, update_status_ticket, update_tickets_issue_admin

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext 

router = Router()

# Обработчик команды /support
@router.message(Command("/sup_adm"), IsAdmin())
async def start_support_message(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(SupAdmStates.sup)
    await message.answer("Действия.", reply_markup=sub_adm_kb)


### Получить тикеты
@router.callback_query(lambda c: c.data == 'Получить тикеты', SupAdmStates.sup)
async def tickets(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupAdmStates.get)
    if await update_tickets_issue_admin(callback_query.from_user.id):
        await callback_query.message.edit_text("Вы взяли тикеты!")
    else:
        await callback_query.message.edit_text("Ошибка")

# Ответ на тикеты
@router.callback_query(lambda c: c.data == 'Активные тикеты', SupAdmStates.sup)
async def tickets(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupAdmStates.get)
    tickets = await get_admin_tickets(callback_query.from_user.id)
    tickets = data['tickets']
    ls_ticket = [i['topic'] for i in tickets]
    await callback_query.message.edit_text("Тикеты", reply_markup=make_kb_list(ls_ticket, "Выйти"))
