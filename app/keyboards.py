from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random

from app.database.requests import get_categories, get_items_by_category

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🛒 Погнали смотреть ковры!', callback_data='catalog')],
    [InlineKeyboardButton(text='🧵 Хочу свой ковёр! ✨', callback_data='zakaz')],
    [InlineKeyboardButton(text='❓ Есть вопросик', callback_data='question')],
    [InlineKeyboardButton(text='💬 Написать нам', callback_data='feedback')],
    [InlineKeyboardButton(text='👀 Кто мы такие?', callback_data='about_us')],
    [InlineKeyboardButton(text='📨 Промокод', callback_data='promo')]
])

order = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📝 Заполнить анкету', callback_data='order')],
    [InlineKeyboardButton(text='🏠 Вернуться домой', callback_data='main')]
])

skip = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⏭️ Пропустить этот шаг', callback_data='skip')]
])

wall_choise = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🧲 Да, хочу повесить на стену', callback_data='wall_yes')],
    [InlineKeyboardButton(text='🛋️ Нет, пусть лежит на полу', callback_data='wall_no')]
])

final_order = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📨 Отправить мою заявку!', callback_data='send_order')],
    [InlineKeyboardButton(text='🔁 Всё заново, я передумал 😅', callback_data='order')],
    [InlineKeyboardButton(text='🏠 Вернуться в главное меню', callback_data='main_new_answer')]
])

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🏡 Вернуться домой', callback_data='main')]
])

questions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🧼 Как ухаживать за ковриком?', callback_data='care')],
    [InlineKeyboardButton(text='💰 Сколько всё это стоит?', callback_data='cost')],
    [InlineKeyboardButton(text='🧠 А как формируется цена?', callback_data='cost_question')],
    [InlineKeyboardButton(text='⏳ Какой срок изготовления коврика?', callback_data='time_work')],
    [InlineKeyboardButton(text='🏠 Вернуться в начало', callback_data='main')]
])

back_to_questions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Назад к другим вопросам', callback_data='question')],
    [InlineKeyboardButton(text='🏡 В главное меню', callback_data='main_new_answer')]
])

promo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📝 Ввести промокод повторно', callback_data='promo')],
    [InlineKeyboardButton(text='🏠 Вернуться домой', callback_data='main')]
])

# Категории и товары — с прикольными подписями
async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.row(InlineKeyboardButton(text=f'🧶 {category.name}', callback_data=f'category_{category.id}'))
    keyboard.row(InlineKeyboardButton(text='🏡 Вернуться домой', callback_data='main'))
    return keyboard.as_markup()

async def get_items(category_id):
    emojis = ['🧶', '🧵', '✂️', '🧑‍🎨', '🎨', '🌈', '🧸', '📌', '🏠', '🧚‍♂️', '📍', '💭', '🌿', '🌟', '🎁']
    all_items = await get_items_by_category(category_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.row(InlineKeyboardButton(text=f'{random.choice(emojis)} {item.name}', callback_data=f'item_{item.id}'))
    keyboard.row(InlineKeyboardButton(text='🔙 Назад к выбору', callback_data='catalog'))
    return keyboard.as_markup()

async def back_to_category(category_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 Вернуться к категории', callback_data=f'category_{category_id}')],
        [InlineKeyboardButton(text='🏡 Вернуться домой', callback_data='main_new_answer')]
    ])

admin_kb_add_item = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить предмет', callback_data='add_item')]
])

