from keyboards.builders import main_keyboard, start_keyboard

from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_command_start(message: types.Message):
    await message.answer("Привет! Я бот, помогу тебе автоматически записываться на спортивные секции в итмо\n"
                         "Введи /reg, чтобы начать пользоваться\n"
                         "/help - команды\n",
                         reply_markup=start_keyboard)

@router.message(Command("help"))
async def start_command_help(message: types.Message):
    await message.answer(
        "Команды:\n"
        "/start - Знакомство с ботом\n"
        "/help - функционал\n"
        "/reg - регитстрация\n"
        "/support - сообщить о проблеме\n"
        "/record - запись на секции\n"
        "/unsub - отписаться от секции\n"
        "/del - удалить все данные о себе\n",
        reply_markup=main_keyboard
    )
