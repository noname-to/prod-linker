from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

from app.data.models import AddressDetails, Coords, Person

class FetchSlots(BaseModel):
    latitude: float
    longitude: float


class CreateMeeting(BaseModel):
    start_time: Optional[datetime]
    confidant: Optional[Person]
    meeting_location_latitude: float
    meeting_location_longitude: float
    meeting_location_details: AddressDetails = Field(AddressDetails())
    comment: Optional[str] = Field(None, max_length=500)


class EditMeeting(BaseModel):
    start_time: datetime
    confidant: Optional[Person]
    meeting_location_latitude: float
    meeting_location_longitude: float
    meeting_location_details: AddressDetails = Field(AddressDetails())
    comment: Optional[str] = Field(None, max_length=500)


class DailySlots(BaseModel):
    day: datetime
    slots: List[datetime]


class RateMeeting(BaseModel):
    rating: int
    comment_rating: Optional[str] = Field(None)
