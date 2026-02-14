from config.settings_bot import bot_config
from routers import commands, admin, support, reg, record, delete, unsub
from record.record import periodic_task

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from middlewares.throttling import MiddlewareAntiSpam
from utils import logger
import asyncio



async def bot_main():
    bot = Bot(token=bot_config.telegram_api_key)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров
    dp.include_router(commands.router)
    dp.include_router(reg.router)
    dp.include_router(delete.router)
    dp.include_router(support.router)
    dp.include_router(admin.router)
    dp.include_router(record.router)
    dp.include_router(unsub.router)

    # Подключение антиспама
    dp.message.middleware(MiddlewareAntiSpam())
    
    print("Bot is running...")
    await asyncio.gather(
        dp.start_polling(bot),
        periodic_task()
        )
        


if __name__ == "__main__":
    asyncio.run(bot_main())


