from routers import commands, admin, support, reg, record, delete, unrec, sup_admin
from record.record import record_main
from utils.logger import *
from bot import bot
from services.ban_storage import BanStorage

from aiogram.fsm.storage.memory import MemoryStorage
from middlewares.throttling import MiddlewareAntiSpam
from aiogram import Dispatcher
import asyncio



async def bot_main():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров
    dp.include_router(commands.router)
    dp.include_router(reg.router)
    dp.include_router(delete.router)
    dp.include_router(support.router)
    dp.include_router(admin.router)
    dp.include_router(record.router)
    dp.include_router(unrec.router)
    dp.include_router(sup_admin.router)

    # Подключение антиспама
    dp.message.middleware(MiddlewareAntiSpam())
    
    print("Bot is running...")
    await BanStorage("storage/ban.json").update()
    await asyncio.gather(
        dp.start_polling(bot),
        record_main()
        )

6
if __name__ == "__main__":
    asyncio.run(bot_main())


