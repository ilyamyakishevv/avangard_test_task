from celery_app import app
from database import async_session 
from services import api_interaction

@app.task
def check_treshold_prices_task():
    import asyncio

    async def run_check():
        async with async_session() as db:
            result = await api_interaction.check_treshold_prices(db)
            print(result)

    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(run_check())