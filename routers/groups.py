from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth
from database import get_db

router = APIRouter(
    prefix="/groups",
    tags=["groups"]
)

@router.post("/", response_model=schemas.GroupOut)
def create_group(group: schemas.GroupCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Check if group name already exists
    existing_group = db.query(models.Group).filter(models.Group.name == group.name).first()
    if existing_group:
        raise HTTPException(status_code=400, detail="Group name already exists")
    
    # Create new group
    db_group = models.Group(
        name=group.name,
        description=group.description,
        avatar_url=group.avatar_url,
        owner_id=current_user.id
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    # Automatically add the creator as a member
    member = models.GroupMember(group_id=db_group.id, user_id=current_user.id)
    db.add(member)
    db.commit()
    
    return db_group

@router.post("/{group_id}/join", response_model=schemas.GroupMemberOut)
def join_group(group_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    # Check if already a member
    existing = db.query(models.GroupMember).filter_by(group_id=group_id, user_id=current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already a member")
    member = models.GroupMember(group_id=group_id, user_id=current_user.id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

@router.get("/my-groups", response_model=List[schemas.GroupOut])
def my_groups(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    memberships = db.query(models.GroupMember).filter_by(user_id=current_user.id).all()
    group_ids = [m.group_id for m in memberships]
    groups = db.query(models.Group).filter(models.Group.id.in_(group_ids)).all() if group_ids else []
    return groups

@router.get("/", response_model=List[schemas.GroupOut])
def get_all_groups(db: Session = Depends(get_db)):
    """Get all groups"""
    groups = db.query(models.Group).all()
    return groups

@router.get("/{group_id}", response_model=schemas.GroupOut)
def get_group(group_id: int, db: Session = Depends(get_db)):
    """Get a specific group by ID"""
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.get("/{group_id}/members", response_model=List[schemas.UserOut])
def group_members(group_id: int, db: Session = Depends(get_db)):
    members = db.query(models.GroupMember).filter_by(group_id=group_id).all()
    user_ids = [m.user_id for m in members]
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all() if user_ids else []
    return users
