from config.settings_bot import bot_config
from filters.filters import IsAdmin
from keyboards.builders import main_keyboard, start_keyboard
from services.ban_storage import BanStorage
from services.postgre_db import del_all_section_data, get_user_data, get_count_user, get_list_users
from record.record import parsing_section
from states.admin_states import AdminStates

from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
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
        "/send - рассылка\n"
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

@router.message(IsAdmin(), Command("send"))
async def admin_command_send(message: types.Message, state: FSMContext):
    """Команда для начала рассылки"""
    await message.answer(
        "📨 Отправьте текст и/или фото для рассылки.\n"
        "Для отмены напишите 'отмена'"
    )
    await state.set_state(AdminStates.waiting_for_content)

@router.message(IsAdmin(), AdminStates.waiting_for_content, F.text.lower() == "отмена")
async def cancel_mailing(message: types.Message, state: FSMContext):
    """Отмена рассылки"""
    await state.clear()
    await message.answer("❌ Рассылка отменена.")

@router.message(IsAdmin(), AdminStates.waiting_for_content)
async def process_mailing_content(message: types.Message, state: FSMContext):
    """Обработка контента для рассылки"""
    if not message.text and not message.photo and not message.document:
        await message.answer("⚠️ Отправьте текст или медиафайл.")
        return
    # Собираем информацию о сообщении
    content = {
        'text': message.text,
        'photo': message.photo[-1].file_id if message.photo else None,
        'caption': message.caption,
        'document': message.document.file_id if message.document else None
    }
    
    # Получаем всех пользователей (замените на вашу логику)
    users = await get_list_users()  # Ваша функция получения всех пользователей
    if not users:
        await message.answer("❌ Нет пользователей для рассылки.")
        await state.clear()
        return
    
    # Счетчики
    sent_count = 0
    failed_count = 0
    
    # Отправляем сообщение о начале рассылки
    await message.answer(f"📤 Начинаю рассылку {len(users)} пользователям...")
    
    # Рассылка
    for user_id in users:
        try:
            if content['photo']:
                # Отправка с фото
                await bot.send_photo(
                    chat_id=user_id,
                    photo=content['photo'],
                    caption=content['text'] or content.get('caption', '')
                )
            elif content['document']:
                # Отправка с документом
                await bot.send_document(
                    chat_id=user_id,
                    document=content['document'],
                    caption=content['text'] or content.get('caption', '')
                )
            else:
                # Отправка только текста
                await bot.send_message(chat_id=user_id, text=content['text'])
            
            sent_count += 1
            
        except Exception as e:
            failed_count += 1
            logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    
    # Итоговый отчет
    await message.answer(
        f"✅ Рассылка завершена!\n"
        f"📨 Отправлено: {sent_count}\n"
        f"❌ Не доставлено: {failed_count}\n"
        f"👥 Всего пользователей: {len(users)}"
    )
    
    logging.info(f"Рассылка завершена. Отправлено: {sent_count}, Ошибок: {failed_count}")
    await state.clear()
    
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
