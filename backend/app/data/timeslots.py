from collections import defaultdict
from datetime import date, datetime, time, timedelta
from math import floor, ceil
from typing import List, Dict, Tuple
from pprint import pprint as print

from app.data import locations, models
from app.data.managers import meeting_manager


async def split_time_into_timeslots(start_time: datetime, end_time: datetime) -> List[datetime]:
    timeslots = []
    current_time = start_time

    while True:
        timeslots.append(current_time)
        current_time += timedelta(minutes=30)
        if current_time > end_time:
            break
    
    return timeslots


async def calc_ltime(previous_meeting: models.Meeting, current_meeting: models.Meeting) -> datetime:
    representative = current_meeting.representative

    travel_time_minutes = await locations.calculate_traveltime_minutes(
        coords_from=previous_meeting.meeting_location,
        coords_to=current_meeting.meeting_location,
        is_car=representative.is_car,
    )

    travel_time_minutes = ceil(travel_time_minutes / 30) * 30

    return current_meeting.start_time - timedelta(minutes=travel_time_minutes)


async def calc_rtime(meeting: models.Meeting) -> datetime:
    representative = meeting.representative

    service_time = ceil((meeting.product.duration_minutes / representative.kpi) / 30) * 30

    return meeting.start_time + timedelta(minutes=service_time)


async def calc_meeting_window_minutes(previous_meeting: models.Meeting, current_meeting: models.Meeting) -> int:
    representative = previous_meeting.representative
    
    travel_time_minutes = await locations.calculate_traveltime_minutes(
        coords_from=previous_meeting.meeting_location,
        coords_to=current_meeting.meeting_location,
        is_car=representative.is_car,
    )

    service_time = current_meeting.product.duration_minutes / representative.kpi
    return ceil((travel_time_minutes + service_time) / 30) * 30


# async def calc_ltime(previous_meeting: models.Meeting, new_meeting: models.Meeting) -> datetime:
#     travel_time_minutes = await locations.calculate_traveltime_minutes(
#         coords_from=previous_meeting.meeting_location,
#         coords_to=new_meeting.meeting_location,
#         is_car=previous_meeting.representative.is_car,
#     )
#     ltime: datetime = previous_meeting.start_time + timedelta(minutes=previous_meeting.product.duration_minutes / previous_meeting.representative.kpi) + timedelta(minutes=travel_time_minutes)
#     adjusted_ltime_minutes = ceil((ltime - datetime.combine(ltime, time.min)).seconds // 60 / 30) * 30
#     # adjusted_ltime_minutes = floor((ltime - datetime.combine(ltime, time.min)).seconds // 60 / 30) * 30
#     adjusted_ltime = datetime.combine(ltime, time.min) + timedelta(minutes=adjusted_ltime_minutes)
#     return adjusted_ltime


# async def calc_rtime(next_meeting: models.Meeting, new_meeting: models.Meeting) -> datetime:
#     travel_time_minutes = await locations.calculate_traveltime_minutes(
#         coords_from=new_meeting.meeting_location,
#         coords_to=next_meeting.meeting_location,
#         is_car=next_meeting.representative.is_car,
#     )

#     rtime: datetime = next_meeting.start_time - timedelta(minutes=travel_time_minutes) - new_meeting.product.duration / next_meeting.representative.kpi
#     adjusted_rtime_minutes = floor((rtime - datetime.combine(rtime, time.min)).seconds / 60 / 30) * 30
#     # adjusted_rtime_minutes = ceil((rtime - datetime.combine(rtime, time.min)).seconds / 60 / 30) * 30
#     adjusted_rtime = datetime.combine(rtime, time.min) + timedelta(minutes=adjusted_rtime_minutes)
#     return adjusted_rtime

async def clear_off_timespans(
    timeslots: List[datetime],
    representative: models.Representative,
) -> List[datetime]:
    current_weekday = timeslots[0].date().weekday()
    date = timeslots[0].date()
    schedules = filter(lambda schedule: schedule.weekday == current_weekday, representative.working_schedules)

    schedules = [
        (
            datetime.combine(date=date, time=time(hour=schedule.start_time_minutes // 60, minute=schedule.start_time_minutes % 60)),
            datetime.combine(date=date, time=time(hour=schedule.end_time_minutes // 60, minute=schedule.end_time_minutes % 60)),
        ) for schedule in schedules
    ]

    cleared_timespans = []

    for timeslot in timeslots:
        # if timeslot fits at least one schedule, then add and break
        for (schedule_start_time, schedule_end_time) in schedules:
            if schedule_start_time < timeslot < schedule_end_time:
                cleared_timespans.append(timeslot)
                break
    
    return cleared_timespans


async def meeting_insertable_slots(representative_meetings: List[models.Meeting], new_meeting: models.Meeting) -> List[models.TimeSlot]:
    representative = representative_meetings[0].representative
    set_meetings_datetimes = {}
    
    set_meetings_datetimes[representative_meetings[0]] = (await calc_ltime(representative_meetings[0], representative_meetings[0]), await calc_rtime(representative_meetings[0]))
    for idx in range(len(representative_meetings) - 1):
        set_meetings_datetimes[representative_meetings[idx + 1]] = (await calc_ltime(representative_meetings[idx], representative_meetings[idx + 1]), await calc_rtime(representative_meetings[idx + 1]))
    last_idx = len(representative_meetings) - 1
    set_meetings_datetimes[representative_meetings[last_idx]] = (await calc_ltime(representative_meetings[-2], representative_meetings[-1]), await calc_rtime(representative_meetings[-1]))

    prev_meeting = representative_meetings[0]

    representative_timespans = await split_time_into_timeslots(
        start_time=datetime.combine(date=prev_meeting.start_time.date(), time=time(hour=9)),
        end_time=datetime.combine(date=prev_meeting.start_time.date(), time=time(hour=21)),
    )

    representative_timespans = await clear_off_timespans(
        timeslots=representative_timespans,
        representative=representative
    )

    for meeting in representative_meetings[1:]:
        new_meeting_tw = await calc_meeting_window_minutes(previous_meeting=prev_meeting, current_meeting=new_meeting)
        nrtime = set_meetings_datetimes[prev_meeting][1] + timedelta(minutes=new_meeting_tw)
        if nrtime > await calc_ltime(new_meeting, meeting):
            removed_timespans = await split_time_into_timeslots(start_time=set_meetings_datetimes[prev_meeting][1], end_time=await calc_ltime(new_meeting, meeting))
            for timespan in removed_timespans:
                if timespan in representative_timespans: representative_timespans.remove(timespan)
        removed_timespans = []

        removed_timespans += await split_time_into_timeslots(start_time=prev_meeting.start_time, end_time=prev_meeting.start_time + timedelta(minutes=ceil(await locations.calculate_traveltime_minutes(prev_meeting.meeting_location, new_meeting.meeting_location, representative.is_car) / 30) * 30) + timedelta(minutes=prev_meeting.product.duration_minutes / representative.kpi) - timedelta(minutes=30))
        
        removed_timespans += await split_time_into_timeslots(start_time=meeting.start_time - timedelta(minutes=ceil(await locations.calculate_traveltime_minutes(new_meeting.meeting_location, meeting.meeting_location, representative.is_car) / 30) * 30), end_time=meeting.start_time)

        for timespan in removed_timespans:
            if timespan in representative_timespans: representative_timespans.remove(timespan)
                
        

        prev_meeting = meeting
    
    available_slots = [models.TimeSlot(dt=dt, representative=representative) for dt in representative_timespans]

    return available_slots
        


# async def meeting_insertable_slots(representative_meetings: List[models.Meeting], new_meeting: models.Meeting) -> List[models.TimeSlot]:
#     representative = representative_meetings[0].representative
#     # available_slots: List[models.TimeSlot] = []

#     previous_meeting = representative_meetings[0]
#     representative_slots = await split_time_into_timeslots(
#         start_time=datetime.combine(date=previous_meeting.start_time.date(), time=time(hour=9)),
#         end_time=datetime.combine(date=previous_meeting.start_time.date(), time=time(hour=20, minute=55)),
#     )
    
#     for i, meeting in enumerate(representative_meetings[1:]):
#         can_be_time = await calc_ltime(previous_meeting=previous_meeting, new_meeting=new_meeting)
#         must_be_time = await calc_rtime(next_meeting=meeting, new_meeting=new_meeting)

#         print('---')
#         print(f'LT CBT {i}: {can_be_time}')
#         print(f'RT MBT {i}: {must_be_time}')

#         if must_be_time < can_be_time:
#             timespans = await split_time_into_timeslots(start_time=must_be_time, end_time=can_be_time) 
#             for timespan in timespans:
#                 if timespan in representative_slots: representative_slots.remove(timespan)

#         # if must_be_time >= can_be_time:
#         #     timespans = await split_time_into_timeslots(start_time=can_be_time, end_time=must_be_time)
#         #     print('AVAILABLE')
#         #     print(can_be_time)
#         #     print(must_be_time)
#         #     available_slots += [models.TimeSlot(dt=dt, representative=representative) for dt in timespans]
        
#         previous_meeting = meeting

#     available_slots = [models.TimeSlot(dt=dt, representative=representative) for dt in representative_slots]

#     return available_slots


async def count_daily_timeslots_for_new_meeting(
    representative: models.Representative,
    daily_representative_meetings: List[models.Meeting],
    new_meeting: models.Meeting,
) -> List[models.TimeSlot]:

    default_user = daily_representative_meetings[0].user
    meeting_date = daily_representative_meetings[0].start_time.date()

    end_day_meeting = models.Meeting(
        user=default_user,
        representative=representative,
        start_time=datetime.combine(meeting_date, time(hour=21)),
        meeting_location=models.Coords(latitude=55.774102, longitude=37.576834),
        meeting_location_details=models.AddressDetails(),
        product=models.Product(
            title='Finish day',
            documents=[],
            specialists=[],
            duration_minutes=0,
        ),
    )
    
    meetings = daily_representative_meetings + [end_day_meeting]

    slots = await meeting_insertable_slots(representative_meetings=meetings, new_meeting=new_meeting)
    
    return slots


async def count_daily_slots(daily_meetings: List[models.Meeting], new_meeting: models.Meeting) -> List[models.TimeSlot]:
    representatives = set([meeting.representative for meeting in daily_meetings])
    slots = []

    for representative in representatives:
        repr_meetings = list(filter(lambda meeting: meeting.representative.id == representative.id, daily_meetings))
        repr_slots = await count_daily_timeslots_for_new_meeting(
            representative=representative,
            daily_representative_meetings=repr_meetings,
            new_meeting=new_meeting
        )

        slots += repr_slots
    
    return slots


async def get_available_timeslots(start_date: date, new_meeting: models.Meeting) -> Dict[datetime, List[models.TimeSlot]]:
    daily_available_timeslots = {}

    for timedelta_days in range(7):
        current_date = start_date + timedelta(days=timedelta_days)
        daily_meetings = await meeting_manager.get_daily_meetings(date=current_date)

        closest_daily_meetings = await locations.get_closest_meetings(
            meetings=daily_meetings,
            location=new_meeting.meeting_location,
        )

        daily_timeslots = await count_daily_slots(
            daily_meetings=closest_daily_meetings,
            new_meeting=new_meeting,
        )
    

        daily_available_timeslots[current_date] = daily_timeslots

    return daily_available_timeslots