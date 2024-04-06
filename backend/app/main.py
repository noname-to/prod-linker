from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, UnionDoc, Document

from app.routers import user_router, meeting_router
from app import MONGO_DSN

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(user_router.router)
app.include_router(meeting_router.router)


@app.on_event('startup')
async def startup_event():
    client = AsyncIOMotorClient(MONGO_DSN)

    # await init_beanie(database='ultinkoff', document_models=[User, Token, Representative, Meeting])
    await init_beanie(
        database=client.get_default_database(),
        document_models=UnionDoc.__subclasses__() + Document.__subclasses__()
    )


@app.get('/ping')
async def ping() -> Dict[str, str]:
    return {'message': 'ok'}

@app.get('/egorloh')
async def restricted() -> Dict[str, str]:
    return {'message': 'restricted'}