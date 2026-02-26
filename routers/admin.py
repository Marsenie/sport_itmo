from config.settings_bot import bot_config
from filters.filters import IsAdmin
from keyboards.builders import main_keyboard, start_keyboard
from services.ban_storage import BanStorage
from services.postgre_db import del_all_section_data, get_user_data, get_count_user
from record.record import parsing_section

from aiogram import Router, types, Bot
from aiogram.filters import Command
import logging

bot = Bot(token=bot_config.telegram_api_key)
router = Router()
ban_storage = BanStorage("storage/ban.json")



@router.message(IsAdmin(), Command("admin"))
async def admin_command_help(message: types.Message):
    await message.answer(
        "Команды:\n"
        "/ban <id> <минуты> - Бан пользователя\n"
        "/pars - парсит секции в бд\n"
        "/ans - отвечать в поддержке\n"
        "/count - кол-во пользователей")

@router.message(IsAdmin(), Command("ban"))
async def admin_command_ban(message: types.Message):
    parts = message.text.split(maxsplit=2)
    user_id, minutes = int(parts[1].strip()), int(parts[2].strip())
    await ban_storage.ban_user(user_id, minutes)
    try:
        await bot.send_message(chat_id=int(user_id), text=f"Вы забанены на {minutes} минут.")
        await message.answer(f"Пользователь {user_id} забанен на {minutes} минут.")
    except:
        await message.answer(f"сообщение о бане не отправлено пользователю, возможно вы ошиблись в id")
    

    logging.info(f"User {user_id} baned.")


@router.message(IsAdmin(), Command("pars"))
async def admin_command_help(message: types.Message):
    if await del_all_section_data():
        await message.answer("Всё удалено из sections")
    else:
        return await message.answer("Произошли ошибки :(")
    user_data = await get_user_data(message.from_user.id)
    email, password = user_data["email"], user_data["password"] 
    try:
        await parsing_section(email, password)
        await message.answer("Добавлены новые записи в sections")
    except Exception as e:
        await message.answer("Произошли ошибки :(")
        raise e

@router.message(IsAdmin(), Command("count"))
async def admin_command_help(message: types.Message):
    count = await get_count_user()
    await message.answer(f"Количество пользователей: {count}")
    user_data = await get_user_data(message.from_user.id)
