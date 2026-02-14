from aiogram.fsm.state import StatesGroup, State

class SupAdmStates(StatesGroup):
    sup = State()
    
    get = State()
    choice = State()
    msg = State()
    state = State()
    confirm = State()
    
