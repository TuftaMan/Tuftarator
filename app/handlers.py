from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, FSInputFile
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from datetime import datetime, timezone
import asyncio


import app.keyboards as kb
from app.states import Order, Promo
from app.database.requests import set_user, get_item

router = Router()


@router.message(CommandStart(), lambda message: (datetime.now(timezone.utc) - message.date).total_seconds() < 10)
async def cmd_start(message:Message, state: FSMContext):
    username = message.from_user.username
    first_name = message.from_user.first_name
    await set_user(message.from_user.id, username)
    await state.clear()
    await message.answer(
        f"Привет, {first_name} 👋\n\n"
        "Добро пожаловать в *Туфтаратор* — бот-помощник по заказу уникальных тафтинговых ковров 🧶✨\n\n"
        "Выбирай, что тебя интересует 👇",
        reply_markup=kb.main,
        parse_mode="Markdown"
    )


@router.callback_query(F.data == 'main')
async def main(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.clear()
    await callback.message.edit_text(
        "🔙 Ты вернулся в *главное меню!*\n\n"
        "Выбирай, что интересно 👇",
        reply_markup=kb.main,
        parse_mode="Markdown"
    )


@router.callback_query(F.data == 'main_new_answer')
async def main(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.delete()
    await asyncio.sleep(0.3)
    await callback.message.answer(
        "🔙 Ты вернулся в *главное меню!*\n\n"
        "Выбирай, что интересно 👇",
        reply_markup=kb.main,
        parse_mode="Markdown"
    )


@router.callback_query(F.data == 'order')
async def cmd_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(Order.photo)
    await callback.message.answer(
        "📸 У тебя есть фотография или эскиз будущего ковра?\n\n"
        "Если да — просто отправь изображение в чат 📥\n"
        "Если нет — нажми *Пропустить*",
        reply_markup=kb.skip,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == 'skip', Order.photo)
async def skip_photo(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.update_data(photo=None)  # Явно сохраняем None как отсутствие фото
    await callback.message.edit_text("🚫 Пропускаем добавление фото!")
    await callback.message.answer(
        "🧠 Есть идеи, каким ты хочешь видеть ковер?\n"
        "Может, определённый стиль, рисунок, настроение? 😍\n"
        "*Опиши* это — вместе с дизайнером мы создадим что-то особенное!",
        parse_mode="Markdown"
    )
    await state.set_state(Order.about)  # Переходим к следующему состоянию


@router.message(Order.about)
async def cmd_get_about(message: Message, state: FSMContext):
    if message.text is not None:
        await state.update_data(about = message.text)
        await message.answer(
            "✏️ Теперь напиши *длину* желаемого ковра\n"
            "📏 Укажи только число в *сантиметрах*\n"
            "_Пример: 50_",
            parse_mode="Markdown"
        )
        await state.set_state(Order.lenght)
    else:
        await message.answer(
            "Пожалуйста, опиши свою идею 🙌 Или напиши 'Пропустить'",
            parse_mode="Markdown"
        )

@router.message(Order.photo)
async def cmd_get_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    #data = await state.get_data() #Создаю переменную где хранится фото
    await message.answer("🖼️ Эскиз сохранён!")
    await message.answer(
        "✏️ Теперь напиши *длину* желаемого ковра\n"
        "📏 Укажи только число в *сантиметрах*\n"
        "_Пример: 50_",
        parse_mode="Markdown"
    )
    await state.set_state(Order.lenght)


@router.message(Order.lenght)
async def cmd_get_len(message: Message, state: FSMContext):
    if message.text.isdigit():
        lenght = int(message.text)  # Конвертируем в число
        # Добавляем проверку на разумный диапазон
        if 30 <= lenght <= 300:  # Пример: ковры от 30см до 3м
            await state.update_data(lenght=lenght)
            await message.answer(
                "Отлично! 🙌 Теперь укажи *ширину* ковра\n"
                "_Просто число в сантиметрах_",
                parse_mode="Markdown"
            )
            await state.set_state(Order.width)
        else:
            await message.answer(
                "🚫 Пожалуйста, укажи *целое число* от 30 до 300 см\n"
                "Пример: 50",
                parse_mode="Markdown"
            )

    else:
        await message.answer(
            "🚫 Пожалуйста, укажи *целое число* от 30 до 300 см\n"
            "Пример: 50",
            parse_mode="Markdown"
        )


@router.message(Order.width)
async def cmd_get_width(message: Message, state: FSMContext):
    if message.text.isdigit():
        width = int(message.text)  # Конвертируем в число
        # Добавляем проверку на разумный диапазон
        if 30 <= width <= 300:  # Пример: ковры от 30см до 3м
            await state.update_data(width=width)
            await message.answer("🎉 Заявка почти готова!\n\n"
                "💡 Ты хочешь, чтобы ковер можно было *вешать на стену*?\n"
                "Выбери один из вариантов ниже 👇",
                reply_markup=kb.wall_choise,
                parse_mode="Markdown")
            await state.set_state(Order.wall)
        else:
            await message.answer(
                "🚫 Пожалуйста, укажи *целое число* от 30 до 300 см\n"
                "Пример: 50",
                parse_mode="Markdown"
            )

    else:
        await message.answer(
            "🚫 Пожалуйста, укажи *целое число* от 30 до 300 см\n"
            "Пример: 50",
            parse_mode="Markdown"
        )

@router.callback_query(F.data.startswith('wall_'))
async def cmd_get_wall(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    if callback.data == 'wall_yes':
        wall_text = '🧱 *С креплением для стены*'
    else:
        wall_text = '🛏️ *Без крепления*'

    await state.update_data(wall = wall_text)

    # await callback.message.answer('Отлично! Твоя заявка заполена:')
    data = await state.get_data()

    print(data)

    if data.get("photo"):
        await callback.message.answer_photo(
            photo=data["photo"],
            caption="📝 *Твоя заявка готова!*\n\n"
            f"📐 Размер: {data['lenght']} × {data['width']} см\n"
            f"🧲 {data['wall']}",
            reply_markup=kb.final_order,
            parse_mode="Markdown"
        )
    else:
        await callback.message.answer(
            "📝 *Твоя заявка готова!*\n\n"
            f"🖌️ Описание: {data['about']}\n"
            f"📐 Размер: {data['lenght']} × {data['width']} см\n"
            f"🧲 {data['wall']}",
            reply_markup=kb.final_order,
            parse_mode="Markdown"
        )
    await callback.answer()


@router.callback_query(F.data == 'zakaz')
async def order(callback:CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(
        "🧵 Хочешь заказать ковер? Заполни небольшую анкету, и мы всё сделаем!\n\n"
        "Если не хочешь ждать — напиши напрямую: @ToxicMaaan\n\n"
        "👇 Нажми кнопку для оформления заказа:",
        reply_markup=kb.order,
        parse_mode="Markdown"
    )


@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(
        "Выбери тип коврика, который тебя интересует:",
        reply_markup=await kb.categories(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.delete()
    await asyncio.sleep(0.5)
    await callback.message.answer('👇 Вот коврики в выбранной категории:',
                                  reply_markup= await kb.get_items(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('item_'))
async def item_handler(callback: CallbackQuery):
    await callback.answer("")
    item = await get_item(callback.data.split('_')[1])
    photo = FSInputFile(f'{item.photo}')
    await asyncio.sleep(0.3)
    await callback.message.delete()
    await callback.message.answer_photo(photo=photo,
                                        caption=f"*{item.name}*\n{item.description}\n\n💸 *Цена:* {item.price}₽",
                                        reply_markup=await kb.back_to_category(item.category),
                                        parse_mode='Markdown'
                                        )


@router.callback_query(F.data == 'send_order')
async def send_order_to_me(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer('')
    data = await state.get_data()
    first_name = callback.from_user.first_name
    username = callback.from_user.username
    tg_id = callback.from_user.id
    if data.get("photo"):
        await bot.send_photo(chat_id=407125211, photo=data["photo"],
                                            caption=f'Заявка от @{username}, Имя - {first_name}, tg_id - {tg_id}'
                                                    f'\n\nРазмер ковра: \nВысота - {data["lenght"]},'
                                                    f'Ширина - {data["width"]}'
                                                    f'\n{data["wall"]}')
    else:
        await bot.send_message(chat_id=407125211, text=f'Заявка от @{username}, Имя - {first_name}, tg_id - {tg_id}\n\nОписание ковра:'
                                      f'{data["about"]}\nРазмер ковра: \n'
                                      f'Высота - {data["lenght"]} см, Ширина - {data["width"]} см\n'
                                      f'{data["wall"]}')

    await callback.message.answer(
        "✅ Заявка отправлена!\n"
        "Мы скоро свяжемся с тобой, чтобы обсудить детали 💬",
        reply_markup=kb.main_menu,
        parse_mode="Markdown"
    )
    await state.clear()
    await callback.answer('')

@router.callback_query(F.data == 'question')
async def questions(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.delete()
    await asyncio.sleep(0.3)
    await callback.message.answer("❓ Часто задаваемые вопросы:", reply_markup=kb.questions)

@router.callback_query(F.data == 'care')
async def care(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.delete()
    await asyncio.sleep(0.3)
    photo_care = FSInputFile('images/care.png')
    await callback.message.answer_photo(photo=photo_care,
        caption="🧼 *Как ухаживать за ковром?* 🧽\n\n"
                "🔹 Первый месяц: чаще пылесосим на *средней* мощности\n"
                "🔹 Пятна: используем *Vanish* для ковров\n"
                "🔹 Глубокая чистка: химчистка раз в год\n\n"
                "📌 Сохрани эту памятку!\n"
                "Остались вопросы? Спрашивай 👇",
        reply_markup=kb.back_to_questions,
        parse_mode="Markdown"
    )


@router.callback_query(F.data == 'cost')
async def carpet_cost(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(
        "💎 *Стоимость ковров*\n\n"
        "Цена зависит от размера:\n"
        "▫️ 50×50 см — 5 000–7 000 ₽\n"
        "▫️ 70×70 см — 8 000–10 000 ₽\n"
        "▫️ 90×90 см — 10 000–12 000 ₽\n\n"
        "✨ *Индивидуальный заказ?*\n"
        "Рассчитаем точную стоимость под твои пожелания!",
        reply_markup=kb.back_to_questions,
        parse_mode="Markdown"
    )


@router.callback_query(F.data == 'cost_question')
async def how_carpet_cost(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(
        "🧮 *Из чего складывается цена?*\n\n"
        "1. *Материалы*:\n   — Пряжа, ткань, клей\n   — Чем больше ковер, тем больше расход\n\n"
        "2. *Сложность дизайна*:\n   — Мелкие детали = больше времени\n\n"
        "3. *Работа мастера*:\n   — Уникальная ручная работа\n\n"
        "💡 Стоимость = Материалы × 2",
        reply_markup=kb.back_to_questions,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == 'time_work')
async def time_to_work(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(
        "⏳ *Срок изготовления коврика* зависит от нескольких факторов — размера, сложности и нашей загруженности.\n\n"
        "В среднем мы справляемся за *10–14 дней*, но иногда получается быстрее 🌟\n"
        "Если нужен *срочный заказ* — просто напиши нам, постараемся ускориться! 🚀",
        reply_markup=kb.back_to_questions,
        parse_mode='Markdown'
    )

@router.callback_query(F.data == 'feedback')
async def cmd_feedback(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(
        "📲 *Связь с нами*\n\n"
        "👨‍🎨 *Мастер*: @ToxicMaaan\n"
        "💌 *Менеджер*: @allo\_eto\_dyomina\n\n"
        "🔹 *Подпишись для вдохновения*:\n"
        "Instagram: [@tuftacraft](https://www.instagram.com/tuftacraft)\n"
        "Telegram: [t.me/tuftacraft](t.me/tuftacraft)",
        reply_markup=kb.main_menu,
        parse_mode="Markdown"
    )


@router.callback_query(F.data == 'about_us')
async def about_us(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(
    "👋 Привет! Мы *Tufta* — молодой бренд из Иркутска 🧶\n\n"
    "Мы создаём *уникальные ковры вручную* в технике тафтинг:\n"
    "▪️ Индивидуальные заказы\n"
    "▪️ Авторские коллекции\n\n"
    "Каждый ковер — это история, которую можно потрогать!",
    reply_markup=kb.main_menu,
    parse_mode="Markdown"
)

@router.callback_query(F.data == 'promo')
async def get_promo(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(Promo.promokode)
    await callback.message.edit_text('💌Введите промокод или нажмите кнопку для выхода в главное меню',
                                     reply_markup=kb.main_menu)

@router.message(Promo.promokode)
async def check_promo(message: Message, state: FSMContext):
    await state.update_data(promokode = message.text)
    data = await state.get_data()
    user_promo = data['promokode'].lower()
    if user_promo == 'промокод':
        await message.answer('Отлично! Промокод активирован\n'
                             'Ты получаешь скидку в размере 1000 рублей на заказ коврика!\n'
                             'Отметь это при заказе ковра или нам в личных сообщениях',
                                reply_markup=kb.main_menu)
        await state.clear()
    else:
        await message.answer('Такого промокода не существует, попробуйте снова...',
                             reply_markup=kb.promo)
        await state.clear()
