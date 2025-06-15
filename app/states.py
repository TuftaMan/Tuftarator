from aiogram.fsm.state import State, StatesGroup

class Order(StatesGroup):
    photo = State()
    about = State()
    width = State()
    lenght = State()
    wall = State()


class Newsletter(StatesGroup):
    letter = State()

class ChannelMessage(StatesGroup):
    letter = State()

class Promo(StatesGroup):
    promokode = State()


class Item(StatesGroup):
    category = State()
    name = State()
    description = State()
    price = State()
    photo = State()

class NameItem(StatesGroup):
    name = State()