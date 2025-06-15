import os
import asyncio
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv


from app.handlers import router
from app.admin import admin
from app.database.models import async_main


from app.autopost import autopost_message
from app.database.scheduler import scheduler


async def on_autopost_bot(bot: Bot):
    existing_jobs = [job.id for job in scheduler.get_jobs()]
    if 'weekly_post' not in existing_jobs:
        # await autopost_message(bot) #сразу отправляет сообщение
        scheduler.add_job(
            autopost_message,
            trigger='interval',
            days=7,  # Интервал 7 дней
            id='weekly_post',
            replace_existing=True,
            args=[bot]  # Передаем бот в задачу
        )
    scheduler.start()  # Запускаем планировщик


async def main():
    load_dotenv()
    await async_main()
    dp = Dispatcher()
    bot = Bot(token=os.getenv('TG_TOKEN'))
    dp.startup.register(startup)
    # await on_autopost_bot(bot) #функция включения автопостинга, выключена
    dp.shutdown.register(shutdown)
    dp.include_routers(router, admin)
    await dp.start_polling(bot)

async def startup(dispatcher: Dispatcher):
    print('Бот запущен')

async def shutdown(dispatcher: Dispatcher):
    print('Бот остановлен')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


