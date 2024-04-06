from typing import List
from datetime import date, datetime, time, timedelta

from app.data import models
from app.data.managers import representative_manager


async def get_daily_meetings(date: date) -> List[models.Meeting]:
    all_representatives = await representative_manager.read_all_representatives()
    tinkoff_meetings = []

    TINKOFF_USER = models.User(
        legal_form=1,
        title='Tinkoff',
        last_name='',
        first_name='',
        inn='7710140679',
        kpp='771301001',
        ogrn=1027739642281,
        address='127287, г. Москва, вн.тер.г. Муниципальный Округ Савеловский, ул. Хуторская 2-я, д. 38А, стр. 26',
        requested_product=models.Product(
            title='Day start',
            documents=[],
            duration_minutes=0,
            specialists=[]
        ),
    )

    for representative in all_representatives:
        tinkoff_meeting = models.Meeting(
            user=TINKOFF_USER,
            representative=representative,
            start_time=datetime.combine(date=date, time=time(hour=9)),
            meeting_location=models.Coords(latitude=55.774102, longitude=37.576834),
            meeting_location_details=models.AddressDetails(),
            product=models.Product(
                title='Day start',
                documents=[],
                duration_minutes=0,
                specialists=[]
            ),
        )
        tinkoff_meetings.append(tinkoff_meeting)

    start_of_day = datetime.combine(date, time.min)
    end_of_day = datetime.combine(date, time.max)
    
    daily_meetings = await models.Meeting.find({
            "start_time": {
                "$gte": start_of_day,
                "$lt": end_of_day
            },
        }, fetch_links=True).to_list()
    
    return tinkoff_meetings + daily_meetings


async def get_weekly_meetings(start_date: date) -> List[models.Meeting]:
    end_date = start_date + timedelta(days=7)
    
    return (
        await models.Meeting.find(
            (start_date <= models.Meeting.start_time)
            & (models.Meeting.start_time <= end_date), fetch_links=True
        ).to_list()
    )


async def get_all_representative_meetings(representative: models.Representative) -> List[models.Meeting]:
    return await models.Meeting.find(models.Meeting.representative == representative, fetch_links=True).to_list()
