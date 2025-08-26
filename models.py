from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Integer, default=1)  # 1=True, 0=False
    last_login = Column(DateTime(timezone=True), nullable=True)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    organizer_id = Column(Integer, nullable=False)  # FK to User.id (add ForeignKey if you want strict FK)


class RSVP(Base):
    __tablename__ = "rsvps"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # FK to User.id
    event_id = Column(Integer, nullable=False)  # FK to Event.id
    status = Column(String, default="going")  # going, interested, not_going
    created_at = Column(DateTime(timezone=True), server_default=func.now())
