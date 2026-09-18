from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
start_kb = [
        [KeyboardButton(text="/reg")],
    ]
start_keyboard = ReplyKeyboardMarkup(keyboard=start_kb,
                               resize_keyboard=False,
                               one_time_keyboard=True)
        
main_kb = [
        [KeyboardButton(text="/record")],
        [KeyboardButton(text="/unrec"), KeyboardButton(text="/help")],
    ]
main_keyboard = ReplyKeyboardMarkup(keyboard=main_kb,
                               resize_keyboard=True,
                               one_time_keyboard=False)


accept_kb = [
        [KeyboardButton(text="/accept")],
    ]
accept_keyboard = ReplyKeyboardMarkup(keyboard=accept_kb,
                               resize_keyboard=False,
                               one_time_keyboard=True)
