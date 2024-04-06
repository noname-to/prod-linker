from datetime import datetime, date, time, timedelta
from typing import Annotated, Dict, List, Tuple

from fastapi import APIRouter, HTTPException, Header

from app.data import models, schemas, locations, timeslots
from app.data.managers import meeting_manager
from app.data import models
from app import notifications

from random import choice


router = APIRouter(prefix='/meeting')


async def validate_meeting_availability(meeting: models.Meeting) -> Tuple[bool, models.TimeSlot]:
    timeslot = meeting.start_time

    available_timeslots = await timeslots.get_available_timeslots(start_date=timeslot.date(), new_meeting=meeting)

    valid_timeslots = []
    
    for atimeslot in available_timeslots[timeslot.date()]:
        if atimeslot.dt == timeslot:
            valid_timeslots.append(atimeslot)
        
    if len(valid_timeslots) == 0:
        return False, None

    return len(valid_timeslots) > 0, choice(valid_timeslots)


@router.post('/meeting_slots')
async def get_available_meeting_timeslots(
    request: schemas.FetchSlots,
    oauth_token: Annotated[str | None, Header()] = None,
) -> List[schemas.DailySlots]:
    db_token = await models.Token.find_one({'token': oauth_token}, fetch_links=True)
    if db_token is None:
        raise HTTPException(status_code=401, detail='Invalid token')

    pseudo_meeting = models.Meeting(
        user=db_token.user,
        confidant=None,
        representative=None,
        start_time=None,
        meeting_location=models.Coords(latitude=request.latitude, longitude=request.longitude),
        meeting_location_details=models.AddressDetails(),
        product=db_token.user.requested_product,
        comment=None
    )

    available_slots = await timeslots.get_available_timeslots(
        start_date=date.today() + timedelta(days=1),
        new_meeting=pseudo_meeting,
    )
    
    normalized_slots = []

    for (day, slots) in available_slots.items():
        if len(slots) == 0:
            continue
        slots = sorted(list(set([slot.dt for slot in slots])))
        normalized_slots.append(dict(day=datetime.combine(date=day, time=time()), slots=slots))
    
    return normalized_slots


@router.post('/create_meeting')
async def create_meeting(meeting: schemas.CreateMeeting, oauth_token: Annotated[str | None, Header()] = None) -> models.Meeting:
    db_token = await models.Token.find_one({'token': oauth_token}, fetch_links=True)
    if db_token is None:
        raise HTTPException(status_code=404, detail='Invalid token')
    
    if meeting.start_time is None:
        raise HTTPException(status_code=400, detail='Time argument must be provided')

    db_user: models.User = db_token.user

    daily_meetings = await meeting_manager.get_daily_meetings(date=meeting.start_time.date())
    closest_meetings = await locations.get_closest_meetings(
        meetings=daily_meetings,
        location=models.Coords(latitude=meeting.meeting_location_latitude, longitude=meeting.meeting_location_longitude),
    )

    db_representative = closest_meetings[0].representative

    db_meeting = models.Meeting(
        user=db_user,
        representative=db_representative,
        start_time=meeting.start_time,
        meeting_location=models.Coords(latitude=meeting.meeting_location_latitude, longitude=meeting.meeting_location_longitude),
        meeting_location_details=meeting.meeting_location_details,
        product=db_user.requested_product,
        comment=meeting.comment,
        confidant=meeting.confidant
    )

    is_valid, valid_timeslot = await validate_meeting_availability(meeting=db_meeting)

    if not is_valid:
        raise HTTPException(status_code=400, detail='Invalid timeslot chosen')
    
    db_user.last_known_location = models.Location(
        coordinates=models.Coords(
            latitude=meeting.meeting_location_latitude,
            longitude=meeting.meeting_location_longitude,
        ),
        address_details=meeting.meeting_location_details,
        comment=meeting.comment
    )

    await db_user.save()

    db_meeting.representative = valid_timeslot.representative
    db_meeting.user = db_user

    await db_meeting.create()

    await notifications.send_new_meeting_notification(
        receiver=db_meeting.user.telegram_id,
        meeting=db_meeting,
    )
    
    return db_meeting


@router.delete('/cancel_meeting/{meeting_id}')
async def cancel_meeting(meeting_id: str,  oauth_token: Annotated[str | None, Header()] = None) -> Dict[str, str]:
    db_token = await models.Token.find_one({'token': oauth_token}, fetch_links=True)
    if db_token is None:
        raise HTTPException(status_code=404, detail='Invalid token')

    meeting = await models.Meeting.get(document_id=meeting_id, fetch_links=True)
    if meeting is None:
        raise HTTPException(status_code=404, detail='No meeting found')
    await meeting.delete()

    return {'message': 'meeting deleted'}


@router.post('/finish_meeting/{meeting_id}')
async def finish_meeting(meeting_id: str, oauth_token: Annotated[str | None, Header()] = None) -> Dict[str, str]:
    db_token = await models.Token.find_one({'token': oauth_token}, fetch_links=True)
    if db_token is None:
        raise HTTPException(status_code=404, detail='Invalid token')

    meeting = await models.Meeting.get(document_id=meeting_id, fetch_links=True)
    if meeting is None:
        raise HTTPException(status_code=404, detail='No meeting found')

    meeting.status = models.StatusEnum.completed
    await meeting.save()
    
    notifications.send_meeting_finished_notification(receiver=meeting.user.telegram_id, meeting=meeting)

    return {'message': 'meeting finished'}


@router.post('/edit_meeting/{meeting_id}')
async def edit_meeting(
    meeting_id: str,
    edit_meeting: schemas.EditMeeting,
    oauth_token: Annotated[str | None, Header()] = None,
) -> models.Meeting:
    db_token = await models.Token.find_one({'token': oauth_token}, fetch_links=True)
    if db_token is None:
        raise HTTPException(status_code=404, detail='Invalid token')
    
    db_meeting = await models.Meeting.get(document_id=meeting_id, fetch_links=True)

    if db_meeting is None:
        raise HTTPException(status_code=404, detail='No meeting found')

    db_user: models.User = db_meeting.user

    if edit_meeting.start_time:
        db_meeting.start_time = edit_meeting.start_time
    
    if edit_meeting.meeting_location_latitude and edit_meeting.meeting_location_longitude:
        db_meeting.meeting_location = models.Coords(latitude=edit_meeting.meeting_location_latitude,
                                                    longitude=edit_meeting.meeting_location_longitude)
    
    if edit_meeting.meeting_location_details:
        db_meeting.meeting_location_details = edit_meeting.meeting_location_details
    
    if edit_meeting.comment:
        db_meeting.comment = edit_meeting.comment

    if edit_meeting.confidant:
        db_meeting.confidant = edit_meeting.confidant

    db_user.last_known_location = models.Location(
        coordinates=models.Coords(
            latitude=edit_meeting.meeting_location_latitude,
            longitude=edit_meeting.meeting_location_longitude,
        ),
        address_details=edit_meeting.meeting_location_details,
        comment=edit_meeting.comment
    )

    await db_user.save()

    db_meeting.user = db_user

    await db_meeting.save()
    
    await notifications.send_new_meeting_notification(
        receiver=db_meeting.user.telegram_id,
        meeting=db_meeting,
    )

    return db_meeting


@router.post('/rate_meeting/{meeting_id}')
async def rate_meeting(
    meeting_id: str,
    rate_meeting: schemas.RateMeeting,
    oauth_token: Annotated[str | None, Header()] = None,
) -> Dict[str, str]:
    db_token = await models.Token.find_one({'token': oauth_token}, fetch_links=True)
    if db_token is None:
        raise HTTPException(status_code=404, detail='Invalid token')
    
    if meeting_id == 'undefined':
        raise HTTPException(status_code=400, detail='meeting_id undefined')

    db_meeting = await models.Meeting.get(document_id=meeting_id, fetch_links=True)
    if db_meeting is None:
        raise HTTPException(status_code=404, detail='No meeting found')

    if not(1 <= rate_meeting.rating <= 5):
        raise HTTPException(status_code=400, detail='Invalid rating provided')

    db_meeting.rating = rate_meeting.rating
    if rate_meeting.comment_rating:
        db_meeting.comment_rating = rate_meeting.comment_rating
    
    await db_meeting.save()

    return {'message': 'meeting successfully rated'}
