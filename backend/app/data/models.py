from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, validator

from beanie import Document, Link

import re

vehicle_regex = re.compile(r"^[АВЕКМНОРСТУХ]\d{3}(?<!000)[АВЕКМНОРСТУХ]{2}\d{2,3}$")


class AttachedDocument(BaseModel):
    title: str = Field(max_length=100)
    filepath: Optional[str] = Field(None, max_length=150)


class Product(BaseModel):
    title: str = Field(max_length=100)
    documents: List[AttachedDocument]
    specialists: List[str]
    duration_minutes: int 


class Coords(BaseModel):
    latitude: float
    longitude: float


class AddressDetails(BaseModel):
    entrance: Optional[str] = Field(None)
    floor: Optional[str] = Field(None)
    room: Optional[str] = Field(None)
    intercom: Optional[str] = Field(None)


class Location(BaseModel):
    coordinates: Coords
    address_details: AddressDetails
    comment: Optional[str] = Field(None)
    

class Person(BaseModel):
    last_name: str = Field('', max_length=50)
    first_name: str = Field('', max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None)
    warrant: Optional[str] = Field(None, max_length=200)
    occupation: Optional[str] = Field(None, max_length=40)
    

class User(Document):
    legal_form: bool  # 0 - ИП; 1 - Юр. лицо
    title: str = Field(max_length=200)
    last_name: str = Field(max_length=50)
    first_name: str = Field(max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    inn: str = Field(pattern=r'^(\d{10}|\d{12})$')
    kpp: Optional[str] = Field(None, pattern=r'^(\d{9})$')
    ogrn: int
    address: str = Field(max_length=500)
    requested_product: Product
    telegram_id: Optional[int] = Field(None)
    last_known_location: Optional[Location] = Field(None)
    default_confidant: Person = Person()


    @validator('ogrn')
    def validate_ogrn(cls, value):
        if len(str(value)) not in {13, 15}:
            raise ValueError('Invalid OGRN')
        return value


class Token(Document):
    token: str = Field(default_factory=lambda: uuid4().hex)
    user: Link[User]


class RepresentativeTimetable(BaseModel):
    weekday: int
    start_time_minutes: int
    end_time_minutes: int


class Representative(Document):
    model_config = ConfigDict(regex_engine='python-re')

    last_name: str = Field(max_length=50)
    first_name: str = Field(max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None)
    avatar_filepath: Optional[str] = Field(None, max_length=150)
    is_car: bool
    vehicle_registration: Optional[str] = Field(None)
    working_schedules: List[RepresentativeTimetable]
    kpi: float = Field(1.0, le=1.5, ge=0.6)

    def __hash__(self) -> int:
        return hash(repr(self))


class StatusEnum(str, Enum):
    assigned = 'assigned'
    completed = 'completed'


class Meeting(Document):    
    user: Link[User]
    confidant: Optional[Person] = Field(None)
    representative: Optional[Link[Representative]]
    start_time: Optional[datetime]
    meeting_location: Coords
    status: StatusEnum = StatusEnum.assigned
    meeting_location_details: AddressDetails = Field(AddressDetails())
    product: Product
    rating: Optional[int] = Field(None)
    comment: Optional[str] = Field(None, max_length=500)
    comment_rating: Optional[str] = Field(None)

    @validator('start_time')
    def validate_start_time(cls, value):
        if not value:
            return None
        if not(9 <= value.hour <= 21):
            raise ValueError('Invalid Start Time')
        return value
    
    @validator('rating')
    def validate_rating(cls, value):
        if value is None:
            return value
    
        if not (1 <= value <= 5):
            raise ValueError('Invalid rating value passed')
        return value

    def __hash__(self) -> int:
        return hash(repr(self))


class TimeSlot(BaseModel):
    dt: datetime
    representative: Representative

    def __hash__(self) -> int:
        return hash(repr(self))
