from database import create_database, async_session

from fastapi import FastAPI
import uvicorn

from api import router as api_router

app = FastAPI()
app.include_router(api_router)


async def startup():
    await create_database()


app.add_event_handler("startup", startup)

db = async_session()


@app.get("/")
async def root():
    return "Hello, application startup complete!"


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
