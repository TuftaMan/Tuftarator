import os
from aiogram import Bot

async def autopost_message(bot: Bot):
    chat_id = os.getenv('CHANNEL_ID')  # Получаем ID канала из переменной окружения
    if chat_id:
        await bot.send_message(chat_id=chat_id,
                               text="🌟 Привет! Не забывай, что ты можешь заказать свой уникальный тафтинговый ковёр прямо сейчас 🧵✨")  # Отправляем сообщение
    else:
        print("Ошибка: Не задан CHANNEL_ID в .env")