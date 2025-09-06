# Event Schemas
from typing import Optional
from datetime import date, time



from pydantic import BaseModel, EmailStr
from datetime import datetime
class GroupMemberCreate(BaseModel):
    group_id: int
    user_id: int

class GroupMemberOut(BaseModel):
    id: int
    group_id: int
    user_id: int
    joined_at: datetime

    class Config:
        from_attributes = True
class GroupCreate(BaseModel):
    name: str
    description: str = None
    avatar_url: str = None

class GroupOut(BaseModel):
    id: int
    name: str
    description: str = None
    owner_id: int
    created_at: datetime
    avatar_url: str = None

    class Config:
        from_attributes = True
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
