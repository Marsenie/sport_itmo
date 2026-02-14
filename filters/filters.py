from aiogram.filters import Filter
from aiogram.types import Message
from config.settings_admins import admins_config

admin_list = admins_config.settings_admins

class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in admin_list

class IsSupportMessage(Filter):
    async def __call__(self, message: Message) -> bool:
        return (message.reply_to_message is not None and 
                message.reply_to_message.from_user.id == bot.id and
                "Support ticket" in message.reply_to_message.text)
