from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
start_kb = [
        [KeyboardButton(text="/reg")],
    ]
start_keyboard = ReplyKeyboardMarkup(keyboard=start_kb,
                               resize_keyboard=True,
                               one_time_keyboard=True)
        
main_kb = [
        [KeyboardButton(text="/record")],
        [KeyboardButton(text="/support"), KeyboardButton(text="/help")],
    ]
main_keyboard = ReplyKeyboardMarkup(keyboard=main_kb,
                               resize_keyboard=True,
                               one_time_keyboard=False)

