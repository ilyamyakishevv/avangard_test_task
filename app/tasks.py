from app.celery_app import app
from database import async_session 
from services import api_interaction

@app.task
def check_treshold_prices_task():
    import asyncio

    async def run_check():
        async with async_session() as db:
            result = await api_interaction.check_treshold_prices(db)
            print(result)

    asyncio.run(run_check())