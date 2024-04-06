import json
from fastapi import APIRouter, HTTPException, Header
from typing import Annotated

from app.data import models

router = APIRouter(prefix='/user')


PATHWAYS = {
    1: 'rs',
    2: 'iekvar',
    3: 'onlinekassa',
}


@router.get('/create_user/{pathway}')
async def generate_user(pathway: int) -> models.Token:
    with open('app/presets.json', 'r') as f:
        data = json.load(f)

    if pathway not in PATHWAYS.keys():
        raise HTTPException(status_code=400, detail='Invalid pathway provided')
    
    db_user = await models.User(**data[PATHWAYS[pathway]]).create()

    db_token = await models.Token(user=db_user).create()

    return db_token


@router.get('/get_meeting')
async def user_meeting_info(oauth_token: Annotated[str | None, Header()]) -> models.Meeting:
    db_token = await models.Token.find_one({'token': oauth_token}, fetch_links=True)
    if db_token is None:
        raise HTTPException(status_code=401, detail='Invalid token')

    db_user = db_token.user

    meeting = await models.Meeting.find_one(models.Meeting.user.id == db_user.id, fetch_links=True)
    
    if meeting is None:
        raise HTTPException(status_code=404, detail='Meeting not found')

    return meeting


@router.get('/get_info')
async def user_info(oauth_token: Annotated[str | None, Header()]) -> models.User:
    db_token = await models.Token.find_one({'token': oauth_token}, fetch_links=True)
    if db_token is None:
        raise HTTPException(status_code=401, detail='Invalid token')
    
    return db_token.user
