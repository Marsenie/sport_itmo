from aiogram.fsm.state import StatesGroup, State

class UnsubStates(StatesGroup):
    unsub = State()
    
    select = State()
    conf_del = State()

    del_all = State()
