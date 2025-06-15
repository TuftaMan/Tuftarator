from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command
from pathlib import Path

from app.states import Newsletter, ChannelMessage, Item, NameItem
from app.database.requests import get_users, update_items, delete_item
import app.keyboards as kb

admin = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [407125211, 1911847051]

#Комманда для сброса машины состояний
@admin.message(Admin(), Command('stop'))
async def stop_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Задача очищена')

#Команда для рассылки в личные сообщения пользователей
@admin.message(Admin(), Command('letter'))
async def newsletter(message: Message, state: FSMContext):
    await state.set_state(Newsletter.letter)
    await message.answer('Введите сообщение для рассылки')


@admin.message(Newsletter.letter)
async def newsletter_message(message: Message, state: FSMContext):
    await state.clear()
    users = await get_users()
    await message.answer('Рассылка началась')
    for user in users:
        try:
            await message.send_copy(chat_id=user.tg_id)
        except Exception as e:
            print(e)
    await message.answer('Рассылка завершена')


#Команда для отправки сообщения в канал Туфтакрафт
@admin.message(Command('channel_message'))
async def set_message_to_channel(message: Message, state: FSMContext):
    await state.set_state(ChannelMessage.letter)
    await message.answer('Введите сообщение для отправки в канал @tuftacraft')


@admin.message(ChannelMessage.letter)
async def send_message_to_channel(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(letter = message.text)
    data = await state.get_data()
    await bot.send_message(chat_id="@tuftacraft", text=f"{data['letter']}")
    await state.clear()
    await message.answer('Сообщение отправлено в канал!')


#Команда для получения списка пользователей бота
@admin.message(Command('users'))
async def get_users_from_db(message: Message):
    await message.answer('Направляю список пользователей:')
    users = await get_users()
    count = 0

    for user in users:
        await message.answer(f'№{user.id}\n'
                             f'ТГ айди - {user.tg_id}\n'
                             f'Юзернейм - {user.username}'
                             )
        count += 1

    await message.answer(f'Вот список из {count} пользователей')


#Команда для добавления ковра в каталог
@admin.message(Command('additem'))
async def add_category(message: Message, state: FSMContext):
    await state.set_state(Item.category)
    await message.answer('Введите категорию товара, цифру 1 или 2\n'
                         '1 - С креплением на стену\n'
                         '2 - Без крепления на стену')

@admin.message(Item.category)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer('Введите имя товара')
    await state.set_state(Item.name)

@admin.message(Item.name)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введи описание')
    await state.set_state(Item.description)

@admin.message(Item.description)
async def add_price(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('Введи цену !только цифру!!')
    await state.set_state(Item.price)

@admin.message(Item.price)
async def add_photo(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer('Отправь фото')
    await state.set_state(Item.photo)

@admin.message(Item.photo)
async def final_item(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    data = await state.get_data()
    await message.answer_photo(photo=data['photo'], caption=f"Категория - {data['category']}\n"
                                                            f"Имя - {data['name']}\n"
                                                            f"Описание - {data['description']}\n"
                                                            f"Цена - {data['price']}", reply_markup=kb.admin_kb_add_item)


async def save_photo(bot, photo_id: str, name: str):
    file = await bot.get_file(photo_id)
    file_path = file.file_path

    destination = Path('images') / f'{name}.png'
    destination.parent.mkdir(parents=True, exist_ok=True)

    await bot.download_file(file_path, destination)
    return destination


@admin.callback_query(F.data == 'add_item')
async def add_item_in_db(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category = data['category']
    name = data['name']
    description = data['description']
    price = int(data['price'])
    photo_id = data['photo']

    bot = callback.bot

    destination = await save_photo(bot, photo_id, name)
    photo = str(destination)
    await update_items(category, name, description, price, photo)


@admin.message(Command('delete'))
async def delete_item_input_name(message: Message, state: FSMContext):
    await state.set_state(NameItem.name)
    await message.answer('Введите название товара, который хотите удалить')

@admin.message(NameItem.name)
async def delete_aprove(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    name = data['name']
    await delete_item(name)
    await message.answer(f'{name} - Товар удален')
    await state.clear()












