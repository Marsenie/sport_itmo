from states.reg_states import RegistrationStates
from services.postgre_db import add_user_data, get_user_data, del_user_data
from record.record import get_isu_and_name

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Router, types

router = Router()
    
# Обработчик команды /reg
@router.message(Command('reg'))
async def cmd_reg(message: types.Message, state: FSMContext):
    if await get_user_data(message.from_user.id) != []:
        await message.answer("Вы уже указали все данные, если хотите их поменять, то сначала сотрите их /del")
        return
    await message.answer("Введите ваш email:")
    await state.set_state(RegistrationStates.waiting_for_email)

# Обработчик ввода email
@router.message(RegistrationStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    # Простая валидация email
    if '@' not in email or '.' not in email:
        await message.answer("Пожалуйста, введите корректный email:")
        return
    
    # Сохраняем email в состоянии
    await state.update_data(email=email)
    
    await message.answer("Теперь введите пароль:")
    await state.set_state(RegistrationStates.waiting_for_password)

# Обработчик ввода пароля
@router.message(RegistrationStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    
    # Получаем данные из состояния
    user_data = await state.get_data()
    email = user_data['email']

    # Предупреждаем об ожидании
    await message.answer("Подождите, проверяем корректность данных.")
    # Получаем информацию о пользователе
    user_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name or "Unknown"
    isu, name = await get_isu_and_name(email, password)
    await state.clear()
    if isu == "":
        await message.answer("Ошибка! Ваши данные не сохранены.")
        return
    # Вызываем вашу функцию для добавления пользователя
    await add_user_data(user_id, email, password, username, isu, name)
    
    await message.answer("Регистрация завершена! Ваши данные сохранены.")
