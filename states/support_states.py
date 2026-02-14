from aiogram.fsm.state import StatesGroup, State

class SupStates(StatesGroup):
    sup = State()
    
    topic = State()
    question = State()
    create_confirm = State()
    response = State()

    
    ticket = State()
    watch_ticket = State()
    msg = State()
    action_confirm = State()
    feedback = State()
    score = State()
    comment = State()
