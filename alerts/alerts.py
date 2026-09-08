from config.settings_bot import bot_config

from bot import bot

async def send_message_to_user(user_id: int, text: str):
    try:
        await bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        print(f"Ошибка: {e}")

async def send_err_record_to_user(user_id, section:str, info:str = 'Отсутвует'):
    await send_message_to_user(user_id,
                               'Попытка записать на секцию не удалась\n'
                               f'Название секции: {section}\n\n'
                               f'Доп информация:\n{info[-700:]}')
                               
async def send_success_record_to_user(user_id, section:str):
    await send_message_to_user(user_id, f'Вы записались на секцию: {section}')
    
async def send_answer_suport(user_id, text:str):
    await send_message_to_user(user_id, text)
