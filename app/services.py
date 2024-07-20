import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session
from config import EXTERNAL_API_ENDPOINT, HEADERS
from crud import currrencies_crud


class ExternalApiInteraction:
    async def get_current_price(self, symbol: str) -> float:
        params = {"symbol": symbol, "convert": "USD"}
        async with httpx.AsyncClient() as client:
            response = await client.get(EXTERNAL_API_ENDPOINT, headers=HEADERS, params=params)
            data = response.json()
            price = data["data"][symbol]["quote"]["USD"]["price"]
        return price

    async def check_treshold_prices(self, db: AsyncSession) -> str:
        results = []
        currencies_pairs = await currrencies_crud.read_all(db=db)
        for pair in currencies_pairs:
            symbol = pair.user_currency
            max_treshold = pair.max_treshold
            min_threshold = pair.min_treshold
            current_price = await self.get_current_price(symbol)
            if current_price > max_treshold:
                results.append(
                    f"Current price of currency {symbol} - {current_price} is upper than your treshold value ({max_treshold})"
                )
            elif current_price < min_threshold:
                results.append(
                    f"Current price of currency {symbol} - {current_price} is lower than your treshold value ({min_threshold})"
                )
        if results:
            return "\n".join(results)
        return "All currency pairs are within the threshold values."


api_interaction = ExternalApiInteraction()


async def main() -> None:
    async with async_session() as db:
        result = await api_interaction.check_treshold_prices(db)
        print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
