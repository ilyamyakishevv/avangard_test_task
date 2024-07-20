import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram import Router

from config import BOT_TOKEN, API_ENDPOINT

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


@router.message(Command(commands=["start"]))
async def send_welcome(message: types.Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Создать пару", callback_data="create_pair")],
            [InlineKeyboardButton(text="Мои пары", callback_data="my_pairs")],
        ]
    )
    await message.answer("Привет! Я бот для управления валютными парами.", reply_markup=keyboard)


@router.callback_query(F.data == "create_pair")
async def process_create_pair(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer("Введите валюту (например, BTC):")
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


@router.callback_query(F.data == "my_pairs")
async def process_my_pairs(callback_query: types.CallbackQuery) -> None:
    user_tg_id = callback_query.from_user.id
    pairs = await fetch_api(f"{user_tg_id}/", "GET")
    if not pairs:
        await bot.send_message(callback_query.from_user.id, "У вас нет созданных пар.")
    for pair in pairs:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Удалить", callback_data=f"delete_pair_{pair['id']}")]
            ]
        )
        await bot.send_message(
            callback_query.from_user.id,
            f"{pair['user_currency']} - Макс: {pair['max_treshold']}, Мин: {pair['min_treshold']}",
            reply_markup=keyboard,
        )


@router.callback_query(F.data.startswith("delete_pair_"))
async def process_delete_pair(callback_query: types.CallbackQuery) -> None:
    pair_id = callback_query.data.split("_")[-1]
    await fetch_api(f"{pair_id}/", "DELETE")
    await bot.send_message(callback_query.from_user.id, "Пара удалена.")


async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
