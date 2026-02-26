from services.validate_sql import validate

from aiogram import types
from aiogram import BaseMiddleware
from collections import defaultdict
from aiogram import types
import time
import asyncio
from services.ban_storage import BanStorage



class MiddlewareAntiSpam(BaseMiddleware):
    def __init__(self, limit_interval=10, max_messages_per_interval=7, ban_time=30):
        self.limit_interval = limit_interval
        self.max_messages = max_messages_per_interval
        self.ban_time = ban_time
        self.user_message_times = defaultdict(list)
        self.ban_storage = BanStorage("storage/ban.json")
        #self.ban_storage.write_all()
        
        super().__init__()

    async def __call__(self, handler, message: types.Message, data: dict):
        await self.ban_storage.update()
        self.banned_users = await self.ban_storage._read_all()
        current_time = time.time()
        user_id = str(message.from_user.id)
        msg = message.text.strip()

        # Проверка бана
        if user_id in self.banned_users:
            if current_time < self.banned_users[user_id]:
                # если забанен
                return await message.answer("Вы забанены.")    
            else:
                # Бан закончился
                del self.banned_users[user_id]
                await self.ban_storage.write_all(self.banned_users)
                self.user_message_times[user_id] = []
                return await handler(message, data)
                

        
        # Очистка старых сообщений
        self.user_message_times[user_id] = [
            t for t in self.user_message_times[user_id] 
            if current_time - t < self.limit_interval
        ]

        # Добавление времени сообщения
        self.user_message_times[user_id].append(current_time)

        # Проверка SQL инъекций
        if not(await validate(msg)):
            # Бан
            await self.ban_storage.ban_user(user_id, msg, 3)
            return await message.answer("Попытка SQL инъекции.\n\nВы забанены до проверки модерацией(не более 2 дней).")
            
          
        # Проверка лимита
        if len(self.user_message_times[user_id]) > self.max_messages:
            # Бан
            await self.ban_storage.ban_user(user_id, msg, 1)
            return await message.answer(f"Слишком много сообщений.\nПодождите 120 секунд.")
        
        return await handler(message, data)
