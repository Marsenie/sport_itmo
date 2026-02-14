from aiogram.fsm.state import StatesGroup, State

class RegistrationStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()
