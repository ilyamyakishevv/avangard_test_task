import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram import Router

from config import BOT_TOKEN, API_ENDPOINT

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()


class CreatePair(StatesGroup):
    waiting_for_currency = State()
    waiting_for_max_price = State()
    waiting_for_min_price = State()


async def fetch_api(endpoint: str, method: str = "GET", data: dict = None) -> None:
    async with aiohttp.ClientSession() as session:
        url = f"{API_ENDPOINT}/{endpoint}"
        if method == "GET":
            async with session.get(url) as response:
                return await response.json()
        elif method == "POST":
            async with session.post(url, json=data) as response:
                return await response.json()
        elif method == "DELETE":
            async with session.delete(url, json=data) as response:
                return await response.json()


def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать пару")],
            [KeyboardButton(text="Мои пары")],
            [KeyboardButton(text="Главное меню")],
        ],
        resize_keyboard=True
    )

@router.message(Command(commands=["start"]))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот для управления валютными парами.", reply_markup=main_menu_keyboard())

@router.message(lambda message: message.text == "Главное меню")
async def process_main_menu(message: types.Message):
     await message.answer("Вы вернулись в главное меню", reply_markup=main_menu_keyboard())

@router.message(lambda message: message.text == "Создать пару")
async def process_create_pair(message: types.Message, state: FSMContext):
    await message.answer("Введите валюту (например, BTC):", reply_markup=main_menu_keyboard())
    await state.set_state(CreatePair.waiting_for_currency)


@router.message(CreatePair.waiting_for_currency)
async def process_currency(message: types.Message, state: FSMContext) -> None:
    await state.update_data(currency=message.text)
    await message.answer("Введите максимальную цену:")
    await state.set_state(CreatePair.waiting_for_max_price)


@router.message(CreatePair.waiting_for_max_price)
async def process_max_price(message: types.Message, state: FSMContext) -> None:
    await state.update_data(max_price=message.text)
    await message.answer("Введите минимальную цену:")
    await state.set_state(CreatePair.waiting_for_min_price)


@router.message(CreatePair.waiting_for_min_price)
async def process_min_price(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    data = {
        "user_currency": user_data["currency"].upper(),
        "max_treshold": float(user_data["max_price"]),
        "min_treshold": float(message.text),
        "user_tg_id": message.from_user.id,
    }
    response = await fetch_api("create_pair/", "POST", data)
    await message.answer(f"Пара {response['user_currency']} - USD создана!")
    await state.clear()


@router.message(lambda message: message.text == "Мои пары")
async def process_my_pairs(message: types.Message):
    user_tg_id = message.from_user.id
    pairs = await fetch_api(f"{user_tg_id}/", "GET")

    for pair in pairs:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Удалить", callback_data=f"delete_pair_{pair['id']}")]
        ])
        await message.answer(
            f"{pair['user_currency']} - Макс: {pair['max_treshold']}, Мин: {pair['min_treshold']}",
            reply_markup=keyboard,
        )

@router.callback_query(lambda callback_query: callback_query.data.startswith('delete_pair_'))
async def process_delete_pair(callback_query: types.CallbackQuery):
    pair_id = callback_query.data.split('_')[-1]
    await fetch_api(f'delete_pair/{pair_id}', 'DELETE')
    await bot.send_message(callback_query.from_user.id, "Пара удалена.", reply_markup=main_menu_keyboard())


async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
