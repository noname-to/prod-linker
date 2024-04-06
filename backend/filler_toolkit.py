import json 
from random import choice, choices, randint
from string import digits
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.data.models import Representative, RepresentativeTimetable
from dotenv import load_dotenv
from os import getenv
from datetime import time
from typing import List

load_dotenv()

MONGO_DSN = getenv('MONGO_DSN')

import asyncio


last_names = ['Скорвцов', 'Черкашин', 'Мамедов', 'Рахут']
first_names = ['Мамут', 'Нарэк', 'Владимир', 'Сейди']
middle_names = ['Эдуардович', 'Ширамед Оглы', 'Денисович', 'Маратович']

vehicle_registration_chars = list('АВЕКМНОРСТУХ')
blyatnye_nomera = ['Х777ХХ77', 'Х777СЕ77', 'О000ОО07', 'М999ЕР96', 'А777АА124', 'В333ОС33', 'В007ОР77']


async def main():
    client = AsyncIOMotorClient(MONGO_DSN)

    await init_beanie(
        database=client.get_default_database(),
        document_models=[Representative]
    )

    for _ in range(2):
        obedi: List[RepresentativeTimetable] = []
        for ch in range(7):
            obedi.append(RepresentativeTimetable(weekday=ch, start_time_minutes=9 * 60, end_time_minutes=(12 + (ch % 2)) * 60))
            obedi.append(RepresentativeTimetable(weekday=ch, start_time_minutes=(13 + (ch % 2)) * 60, end_time_minutes=21 * 60))

        abc = f'{choice(vehicle_registration_chars)}{"".join(choices(digits, k=3))}{"".join(choices(vehicle_registration_chars, k=2))}{"".join(choices(digits, k=2))}' if randint(0, 10) < 5 else {choice(blyatnye_nomera)}

        newchelik = await Representative(
            last_name=choice(last_names),
            first_name=choice(first_names),
            middle_name=choice(middle_names),
            is_car=True,
            vehicle_registration=''.join(list(abc)),
            kpi=randint(60, 120) / 100,
            phone_number=f'+7999555{randint(1000, 9999)}',
            working_schedules=obedi,
            avatar_filepath=f'static/p{randint(1, 6)}.jpg'
        ).create()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

loop.close()