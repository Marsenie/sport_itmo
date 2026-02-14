from aiogram.fsm.state import StatesGroup, State

class DelStates(StatesGroup):
    waiting_phrase = State()
