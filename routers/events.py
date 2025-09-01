from fastapi import File, UploadFile
# Upload event banner endpoint

import os
import time
from typing import Optional

from supabase import create_client
import boto3

session = boto3.session.Session()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Helper to save banner to Supabase Storage or local
def save_banner(file, event_id: int) -> Optional[str]:
    """
    Saves a file to Supabase Storage bucket 'banners' if configured, else to local uploads/ folder.
    Returns the public URL or local path.
    """
    timestamp = int(time.time())
    ext = os.path.splitext(file.filename)[-1]
    filename = f"event_{event_id}_{timestamp}{ext}"
    bucket_name = "banners"
    if supabase:
        file.file.seek(0)
        content = file.file.read()
        res = supabase.storage.from_(bucket_name).upload(filename, content, {"content-type": file.content_type})
        if res.get("error"):
            print(f"Supabase upload failed: {res['error']['message']}")
            file.file.seek(0)  # Reset file pointer for local save
        else:
            public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
            return public_url['publicURL'] if 'publicURL' in public_url else None
    # Fallback: save to local uploads/
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    local_path = os.path.join(upload_dir, filename)
    with open(local_path, "wb") as out_file:
        out_file.write(file.file.read())
    return local_path
    # Fallback: save to local uploads/
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    local_path = os.path.join(upload_dir, filename)
    with open(local_path, "wb") as out_file:
        out_file.write(file.file.read())
    return local_path


# RSVP endpoint: POST /events/{event_id}/rsvp


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List


# RSVP endpoint: POST /events/{id}/rsvp

from datetime import datetime

import models, schemas, auth
from database import get_db

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

@router.post("/{event_id}/upload", response_model=schemas.EventResponse)
def upload_event_banner(event_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    # Only organizer can upload banner
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to upload banner for this event")
    banner_url = save_banner(file, event_id)
    event.banner_url = banner_url
    db.commit()
    db.refresh(event)
    # Compose RSVP info for response
    rsvp_count = db.query(models.RSVP).filter_by(event_id=event_id, status="yes").count()
    rsvp = db.query(models.RSVP).filter_by(event_id=event_id, user_id=current_user.id).first()
    rsvp_status = rsvp.status if rsvp else None
    return schemas.EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        date=event.date,
        time=datetime.strptime(event.time, "%H:%M:%S").time(),
        location=event.location,
        organizer=schemas.UserOut.from_orm(event.organizer),
        created_at=event.created_at,
        banner_url=event.banner_url,
        rsvp_count=rsvp_count,
        rsvp_status=rsvp_status
    )


@router.post("/{event_id}/rsvp", response_model=schemas.RSVPResponse)
def rsvp_event(event_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    rsvp = db.query(models.RSVP).filter_by(user_id=current_user.id, event_id=event_id).first()
    if rsvp:
        rsvp.status = "yes"
    else:
        rsvp = models.RSVP(user_id=current_user.id, event_id=event_id, status="yes")
        db.add(rsvp)
    db.commit()
    db.refresh(rsvp)
    return schemas.RSVPResponse.from_orm(rsvp)



# Cancel RSVP endpoint: DELETE /events/{event_id}/rsvp
@router.delete("/{event_id}/rsvp")
def cancel_rsvp(event_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    rsvp = db.query(models.RSVP).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not rsvp:
        raise HTTPException(status_code=404, detail="RSVP not found")
    db.delete(rsvp)
    db.commit()
    return {"success": True}

# List all events the current user registered for
@router.get("/my-registrations", response_model=List[schemas.EventResponse])
def my_registrations(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    rsvps = db.query(models.RSVP).filter_by(user_id=current_user.id).all()
    event_ids = [rsvp.event_id for rsvp in rsvps]
    events = db.query(models.Event).filter(models.Event.id.in_(event_ids)).all() if event_ids else []
    return [
        schemas.EventResponse(
            id=e.id,
            title=e.title,
            description=e.description,
            date=e.date,
            time=datetime.strptime(e.time, "%H:%M:%S").time(),
            location=e.location,
            organizer=schemas.UserOut.from_orm(e.organizer),
            created_at=e.created_at,
            banner_url=e.banner_url
        ) for e in events
    ]
    
    
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
        created_at=db_event.created_at,
        banner_url=db_event.banner_url
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
            created_at=e.created_at,
            banner_url=e.banner_url
        ) for e in events
    ]
    

@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    rsvp_count = db.query(models.RSVP).filter_by(event_id=event_id, status="yes").count()
    rsvp = db.query(models.RSVP).filter_by(event_id=event_id, user_id=current_user.id).first()
    rsvp_status = rsvp.status if rsvp else None
    return schemas.EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        date=event.date,
        time=datetime.strptime(event.time, "%H:%M:%S").time(),
        location=event.location,
        organizer=schemas.UserOut.from_orm(event.organizer),
        created_at=event.created_at,
        banner_url=event.banner_url,
        rsvp_count=rsvp_count,
        rsvp_status=rsvp_status
    )

# List users by RSVP status for an event
@router.get("/{event_id}/rsvps")
def list_event_rsvps(event_id: int, db: Session = Depends(get_db)):
    rsvps = db.query(models.RSVP).filter(models.RSVP.event_id == event_id).all()
    users_by_status = {"yes": [], "no": [], "maybe": []}
    for rsvp in rsvps:
        if rsvp.status in users_by_status:
            user = db.query(models.User).filter(models.User.id == rsvp.user_id).first()
            if user:
                users_by_status[rsvp.status].append({
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                })
    return users_by_status
