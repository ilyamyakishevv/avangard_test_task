import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from config import EXTERNAL_API_ENDPOINT, HEADERS
from crud import currrencies_crud
from database import async_session
from telegram_bot import bot



class ExternalApiInteraction:
    async def get_current_price(self, symbol: str) -> float:
        params = {"symbol": symbol, "convert": "USD"}
        async with httpx.AsyncClient() as client:
            response = await client.get(EXTERNAL_API_ENDPOINT, headers=HEADERS, params=params)
            data = response.json()
            price = data["data"][symbol]["quote"]["USD"]["price"]
        return price
    
    async def send_telegram_notification(
            self,
            user_tg_id: int, 
            message: str) -> None:
        await bot.send_message(chat_id=user_tg_id, text=message)

    async def check_treshold_prices(self, db: AsyncSession) -> str:
        currencies_pairs = await currrencies_crud.read_all(db=db)
        for pair in currencies_pairs:
            symbol = pair.user_currency
            max_treshold = pair.max_treshold
            min_threshold = pair.min_treshold
            current_price = await self.get_current_price(symbol)
            if current_price > max_treshold:
                message = (f"Текущая цена валюты {symbol} - {current_price} выше чем ваше пороговое значение ({max_treshold})")
                await self.send_telegram_notification(pair.user_tg_id, message)
            elif current_price < min_threshold:
                message = f"Текущая цена валюты {symbol} - {current_price} ниже чем ваше пороговое значение ({min_threshold})"
                await self.send_telegram_notification(pair.user_tg_id, message)
    

api_interaction = ExternalApiInteraction()
