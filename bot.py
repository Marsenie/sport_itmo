from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession


from config.settings_bot import bot_config


#from proxy.proxy import RotatingProxySession
#session = RotatingProxySession(get_proxy_func=get_proxy_list,refresh_interval=600)
session = AiohttpSession(proxy=bot_config.PROXY_URL)
bot = Bot(token=bot_config.telegram_api_key, session=session)

