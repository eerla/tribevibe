
from pydantic import BaseModel, EmailStr
from datetime import datetime

# RSVP Schemas
class RSVPResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# Event Schemas
from typing import Optional
from datetime import date, time

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    date: date
    time: time
    location: str

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    date: date
    time: time
    location: str

    organizer: UserOut
    created_at: datetime
    banner_url: Optional[str] = None
    rsvp_count: int = 0
    rsvp_status: Optional[str] = None

    class Config:
        from_attributes = True
