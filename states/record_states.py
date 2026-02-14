from aiogram.fsm.state import StatesGroup, State


class RecordStates(StatesGroup):
    PLACE = State()
    DAY = State()
    TIME = State()
    WEEK = State()
    TEACHER_SECTION = State()
    CONFIRMATION = State()

    SECTION = State()
    COACH = State()
