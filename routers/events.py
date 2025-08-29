from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import models, schemas, auth
from database import get_db

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

@router.post("/", response_model=schemas.EventResponse)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_event = models.Event(
        title=event.title,
        description=event.description,
        date=event.date,
        time=event.time.strftime("%H:%M:%S"),
        location=event.location,
        organizer_id=current_user.id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return schemas.EventResponse(
        id=db_event.id,
        title=db_event.title,
        description=db_event.description,
        date=db_event.date,
        time=datetime.strptime(db_event.time, "%H:%M:%S").time(),
        location=db_event.location,
        organizer=schemas.UserOut.from_orm(db_event.organizer),
        created_at=db_event.created_at
    )

@router.get("/", response_model=List[schemas.EventResponse])
def list_events(db: Session = Depends(get_db)):
    events = db.query(models.Event).order_by(models.Event.date).all()
    return [
        schemas.EventResponse(
            id=e.id,
            title=e.title,
            description=e.description,
            date=e.date,
            time=datetime.strptime(e.time, "%H:%M:%S").time(),
            location=e.location,
            organizer=schemas.UserOut.from_orm(e.organizer),
            created_at=e.created_at
        ) for e in events
    ]

@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return schemas.EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        date=event.date,
        time=datetime.strptime(event.time, "%H:%M:%S").time(),
        location=event.location,
        organizer=schemas.UserOut.from_orm(event.organizer),
        created_at=event.created_at
    )
