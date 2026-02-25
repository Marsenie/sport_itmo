from aiogram.fsm.state import StatesGroup, State

class SupAdmStates(StatesGroup):
    sup = State()

    get_tickets = State()
    
    get = State()
    choice = State()
    msg = State()
    state = State()
    confirm_msg = State()
    confirm = State()
    close = State()
    
