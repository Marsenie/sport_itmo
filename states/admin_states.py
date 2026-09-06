from aiogram.fsm.state import StatesGroup, State

class AdminStates(StatesGroup):
    waiting_for_content = State()
