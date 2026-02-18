from aiogram.utils.keyboard import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup

place_kb_list = [
    [InlineKeyboardButton(text='Ломо', callback_data='Ломо'), InlineKeyboardButton(text='Вязьма', callback_data='Вяземский')],
    [InlineKeyboardButton(text='онлайн', callback_data='онлайн'), InlineKeyboardButton(text='Другие', callback_data='Другие')],
    [InlineKeyboardButton(text='Назад', callback_data='Назад')]
]
place_kb = InlineKeyboardMarkup(inline_keyboard=place_kb_list)


day_kb_list = [
    [InlineKeyboardButton(text='Пн', callback_data='1'), InlineKeyboardButton(text='Вт', callback_data='2'), InlineKeyboardButton(text='Ср', callback_data='3')],
    [InlineKeyboardButton(text='Чт', callback_data='4'), InlineKeyboardButton(text='Пт', callback_data='5'), InlineKeyboardButton(text='Сб', callback_data='6')],
    [InlineKeyboardButton(text='Назад', callback_data='Назад')]
]
day_kb = InlineKeyboardMarkup(inline_keyboard=day_kb_list)


time_kb_list = [
    [InlineKeyboardButton(text='8-9', callback_data='1'), InlineKeyboardButton(text='9-11', callback_data='2'), InlineKeyboardButton(text='11-13', callback_data='3')],
    [InlineKeyboardButton(text='13-15', callback_data='4'), InlineKeyboardButton(text='15-17', callback_data='5'), InlineKeyboardButton(text='17-19', callback_data='6')],
    [InlineKeyboardButton(text='19-21', callback_data='7'), InlineKeyboardButton(text='21-23', callback_data='8')],
    [InlineKeyboardButton(text='Назад', callback_data='Назад')]
]
time_kb = InlineKeyboardMarkup(inline_keyboard=time_kb_list)


week_kb_list = [
    [InlineKeyboardButton(text='Чёт', callback_data='1'), InlineKeyboardButton(text='Нечёт', callback_data='0')],
    [InlineKeyboardButton(text='Каждую', callback_data='2')],
    [InlineKeyboardButton(text='Назад', callback_data='Назад')]
]
week_kb = InlineKeyboardMarkup(inline_keyboard=week_kb_list)

support_kb_list = [
    [InlineKeyboardButton(text='Обращения', callback_data='Обращения')],
    [InlineKeyboardButton(text='Создать обращение', callback_data='Создать обращение')]
]
support_kb = InlineKeyboardMarkup(inline_keyboard=support_kb_list)

small_sup_kb_list = [
    [InlineKeyboardButton(text='Обращения', callback_data='Обращения')],
]
small_sup_kb = InlineKeyboardMarkup(inline_keyboard=small_sup_kb_list)

ticket_kb_list = [
    [InlineKeyboardButton(text='Закрыть обращение', callback_data='Закрыть обращение')],
    [InlineKeyboardButton(text='Новое сообщение', callback_data='Новое сообщение')],
    [InlineKeyboardButton(text='Назад', callback_data='Назад')]
]
ticket_kb = InlineKeyboardMarkup(inline_keyboard=ticket_kb_list)

back_kb_list = [
    [InlineKeyboardButton(text='Назад', callback_data='Назад')]
]
back_kb = InlineKeyboardMarkup(inline_keyboard=back_kb_list)

confirm_kb_list = [
    [InlineKeyboardButton(text='Подтвердить', callback_data='Подтвердить')],
    [InlineKeyboardButton(text='Назад', callback_data='Назад')]
]
confirm_kb = InlineKeyboardMarkup(inline_keyboard=confirm_kb_list)

feedback_kb_list = [
    [InlineKeyboardButton(text='Оценить поддержку', callback_data='Оценить поддержку')]
]
feedback_kb = InlineKeyboardMarkup(inline_keyboard=feedback_kb_list)

score_kb_list = [ [InlineKeyboardButton(text=str(i), callback_data=str(i))] for i in range(1,6)]
score_kb = InlineKeyboardMarkup(inline_keyboard=score_kb_list)

unsub_kb_list = [
    [InlineKeyboardButton(text='секции', callback_data='секции')],
    [InlineKeyboardButton(text='всех секций', callback_data='всех секций')]
]
unsub_kb = InlineKeyboardMarkup(inline_keyboard=unsub_kb_list)

sub_adm_kb_list = [
    [InlineKeyboardButton(text='Получить тикеты', callback_data='Получить тикеты')],
    [InlineKeyboardButton(text='Активные тикеты', callback_data='Активные тикеты')]
]
sub_adm_kb = InlineKeyboardMarkup(inline_keyboard=sub_adm_kb_list)

def make_kb_list(ls, last_btn):
    kb_list = []
    for i in range(len(ls)):
        kb_list.append([InlineKeyboardButton(text=f'{ls[i]}', callback_data=str(i))])
    kb_list.append([InlineKeyboardButton(text=last_btn, callback_data=last_btn), InlineKeyboardButton(text=f'Назад', callback_data='Назад')])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return kb

