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
    # upload_dir = os.path.join(os.getcwd(), "uploads")
    # os.makedirs(upload_dir, exist_ok=True)
    # local_path = os.path.join(upload_dir, filename)
    # with open(local_path, "wb") as out_file:
    #     out_file.write(file.file.read())
    # return local_path


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
        category=event.category,
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
            category=e.category,
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
        category=event.category,
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
        category=db_event.category,
        organizer=schemas.UserOut.from_orm(db_event.organizer),
        created_at=db_event.created_at,
        banner_url=db_event.banner_url
    )

@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(
    event_id: int, 
    event_update: schemas.EventUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Update an event. Only the event organizer can update their event.
    All fields are optional - only provided fields will be updated.
    
    Time format: Accepts both "HH:MM:SS" and ISO format like "2025-09-08T02:01:44.542Z"
    """
    try:
        # Validate event_id
        if not isinstance(event_id, int) or event_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid event ID. Must be a positive integer.")
        
        # Find the event
        try:
            event = db.query(models.Event).filter(models.Event.id == event_id).first()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database error while retrieving event.")
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Check if current user is the organizer
        if event.organizer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this event. Only the event organizer can update their event.")
        
        # Update only the fields that are provided
        try:
            update_data = event_update.dict(exclude_unset=True)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid request data format.")
        
        # Validate that at least one field is provided for update
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update. At least one field must be specified.")
        
        # Process each field with proper validation
        for field, value in update_data.items():
            try:
                if field == "date" and value is not None:
                    # Handle date field - convert string to date object
                    if isinstance(value, str):
                        # Validate date string format
                        if not value.strip():
                            raise ValueError("Date cannot be empty")
                        # Parse the date string
                        parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
                        # Validate that the date is not in the past (optional business rule)
                        if parsed_date < datetime.now().date():
                            raise ValueError("Event date cannot be in the past")
                        setattr(event, field, parsed_date)
                    else:
                        setattr(event, field, value)
                        
                elif field == "time" and value is not None:
                    # Handle time field - it should be a string in HH:MM:SS format
                    if isinstance(value, str):
                        if not value.strip():
                            raise ValueError("Time cannot be empty")
                        # Validate and format the time string
                        try:
                            # Try to parse the time to validate format
                            if "T" in value:  # Handle ISO format like "02:01:44.542Z"
                                # Extract just the time part
                                time_part = value.split("T")[1].split("Z")[0].split(".")[0]
                                # Validate the extracted time format
                                datetime.strptime(time_part, "%H:%M:%S")
                                setattr(event, field, time_part)
                            else:
                                # Validate standard HH:MM:SS format
                                datetime.strptime(value, "%H:%M:%S")
                                setattr(event, field, value)
                        except ValueError as ve:
                            raise ValueError(f"Invalid time format. Use HH:MM:SS or ISO format. Error: {str(ve)}")
                    else:
                        # If it's not a string, convert to string
                        setattr(event, field, str(value))
                        
                elif field == "title" and value is not None:
                    # Validate title
                    if not isinstance(value, str) or not value.strip():
                        raise ValueError("Title must be a non-empty string")
                    if len(value.strip()) > 200:  # Reasonable title length limit
                        raise ValueError("Title must be 200 characters or less")
                    setattr(event, field, value.strip())
                    
                elif field == "description" and value is not None:
                    # Validate description
                    if value is not None and not isinstance(value, str):
                        raise ValueError("Description must be a string")
                    if value and len(value) > 2000:  # Reasonable description length limit
                        raise ValueError("Description must be 2000 characters or less")
                    setattr(event, field, value.strip() if value else None)
                    
                elif field == "location" and value is not None:
                    # Validate location
                    if not isinstance(value, str) or not value.strip():
                        raise ValueError("Location must be a non-empty string")
                    if len(value.strip()) > 500:  # Reasonable location length limit
                        raise ValueError("Location must be 500 characters or less")
                    setattr(event, field, value.strip())
                    
                elif field == "category" and value is not None:
                    # Validate category
                    if value is not None and not isinstance(value, str):
                        raise ValueError("Category must be a string")
                    if value and len(value.strip()) > 100:  # Reasonable category length limit
                        raise ValueError("Category must be 100 characters or less")
                    setattr(event, field, value.strip() if value else None)
                    
                else:
                    # For any other fields, set them directly
                    setattr(event, field, value)
                    
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=f"Validation error for field '{field}': {str(ve)}")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing field '{field}': {str(e)}")
        
        # Save changes to database
        try:
            db.commit()
            db.refresh(event)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Database error while saving changes. Please try again.")
        
        # Get RSVP info for response
        try:
            rsvp_count = db.query(models.RSVP).filter_by(event_id=event_id, status="yes").count()
            rsvp = db.query(models.RSVP).filter_by(event_id=event_id, user_id=current_user.id).first()
            rsvp_status = rsvp.status if rsvp else None
        except Exception as e:
            # If RSVP query fails, continue with default values
            rsvp_count = 0
            rsvp_status = None
        
        # Build response
        try:
            return schemas.EventResponse(
                id=event.id,
                title=event.title,
                description=event.description,
                date=event.date,
                time=datetime.strptime(event.time, "%H:%M:%S").time(),
                location=event.location,
                category=event.category,
                organizer=schemas.UserOut.from_orm(event.organizer),
                created_at=event.created_at,
                banner_url=event.banner_url,
                rsvp_count=rsvp_count,
                rsvp_status=rsvp_status
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error building response. Please try again.")
            
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")

@router.get("/", response_model=List[schemas.EventResponse])
def list_events(
    city: Optional[str] = None,
    category: Optional[str] = None,
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of events with optional filters:
    - city: Filter by city (searches in location field)
    - category: Filter by event category
    - date: Filter by date (YYYY-MM-DD format)
    """
    query = db.query(models.Event)
    
    # Apply filters
    if city:
        query = query.filter(models.Event.location.ilike(f"%{city}%"))
    
    if category:
        query = query.filter(models.Event.category.ilike(f"%{category}%"))
    
    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(models.Event.date == filter_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    events = query.order_by(models.Event.date).all()
    
    return [
        schemas.EventResponse(
            id=e.id,
            title=e.title,
            description=e.description,
            date=e.date,
            time=datetime.strptime(e.time, "%H:%M:%S").time(),
            location=e.location,
            category=e.category,
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
        category=event.category,
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

# Organizer endpoints
@router.get("/organizers/me/events", response_model=List[schemas.EventResponse])
def get_my_events(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Get all events created by the current user (organizer).
    Returns events ordered by date (upcoming first).
    """
    try:
        # Get all events created by the current user
        events = db.query(models.Event).filter(
            models.Event.organizer_id == current_user.id
        ).order_by(models.Event.date).all()
        
        # Build response with RSVP information
        result = []
        for event in events:
            try:
                # Get RSVP count for this event
                rsvp_count = db.query(models.RSVP).filter_by(
                    event_id=event.id, status="yes"
                ).count()
                
                # Get current user's RSVP status for this event
                rsvp = db.query(models.RSVP).filter_by(
                    event_id=event.id, user_id=current_user.id
                ).first()
                rsvp_status = rsvp.status if rsvp else None
                
                result.append(schemas.EventResponse(
                    id=event.id,
                    title=event.title,
                    description=event.description,
                    date=event.date,
                    time=datetime.strptime(event.time, "%H:%M:%S").time(),
                    location=event.location,
                    category=event.category,
                    organizer=schemas.UserOut.from_orm(event.organizer),
                    created_at=event.created_at,
                    banner_url=event.banner_url,
                    rsvp_count=rsvp_count,
                    rsvp_status=rsvp_status
                ))
            except Exception as e:
                # If there's an error with a specific event, skip it and continue
                continue
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving your events. Please try again.")

@router.get("/organizers/{organizer_id}", response_model=schemas.UserOut)
def get_organizer_profile(organizer_id: int, db: Session = Depends(get_db)):
    """
    Get organizer profile by ID.
    Returns basic organizer information.
    """
    try:
        # Validate organizer_id
        if not isinstance(organizer_id, int) or organizer_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid organizer ID. Must be a positive integer.")
        
        # Find the organizer
        organizer = db.query(models.User).filter(models.User.id == organizer_id).first()
        
        if not organizer:
            raise HTTPException(status_code=404, detail="Organizer not found")
        
        # Check if the user has created any events (optional validation)
        event_count = db.query(models.Event).filter(models.Event.organizer_id == organizer_id).count()
        
        # Return organizer profile
        return schemas.UserOut(
            id=organizer.id,
            name=organizer.name,
            email=organizer.email,
            created_at=organizer.created_at
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving organizer profile. Please try again.")
