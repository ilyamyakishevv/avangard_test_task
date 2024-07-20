from celery_app import app
from database import async_session  # Импортируйте вашу сессию из настроек базы данных
from services import ExternalApiInteraction

@app.task
def check_treshold_prices_task():
    import asyncio

    async def run_check():
        async with async_session() as db:
            api_interaction = ExternalApiInteraction()
            result = await api_interaction.check_treshold_prices(db)
            print(result)

    asyncio.run(run_check())