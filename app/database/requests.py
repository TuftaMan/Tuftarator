from app.database.models import async_session, User, Category, Item
from sqlalchemy import select, update, delete


async def set_user(tg_id, username):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            if not username:
                username = None

                session.add(User(tg_id=tg_id, username=username))
                await session.commit()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_items_by_category(category_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category == category_id))


async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))


async def get_users():
    async with async_session() as session:
        return await session.scalars(select(User))


async def update_items(category, name, description, price, photo):
    async with async_session() as session:
        session.add(Item(category=category, name=name, description=description, price=price, photo=photo))
        await session.commit()


async def delete_item(name):
    async with async_session() as session:
        result = await session.execute(select(Item).where(Item.name == name))
        item = result.scalar_one_or_none()

        if item:
            await session.delete(item)
            await session.commit()
            print(f"Удалён: {item}")
        else:
            print("Товар не найден")



