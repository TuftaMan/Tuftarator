import os

from sqlalchemy import String, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncAttrs, create_async_engine

from dotenv import load_dotenv

load_dotenv()

# engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=True)
engine = create_async_engine(url=os.getenv('DB_URL'), echo=True)

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column((String(50)), nullable=True)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(25))


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    name: Mapped[str] = mapped_column(String(25))
    description: Mapped[str] = mapped_column(String(512))
    price: Mapped[int]
    photo: Mapped[str] = mapped_column(String(50))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
