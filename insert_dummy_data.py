#!/usr/bin/env python3
"""
Dummy Data Insertion Script for TribeVibe API

This script creates comprehensive dummy data for all the APIs in the project:
- Users (with proper password hashing)
- Groups (with different owners)
- Group Memberships
- Events (with different organizers)
- RSVPs (with various statuses)

Usage:
    python insert_dummy_data.py

Requirements:
    - Database must be set up and running
    - All dependencies installed (see requirements.txt)
    - Environment variables configured (.env file)
"""

import os
import sys
from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Add the current directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from models import Base, User, Group, GroupMember, Event, RSVP
import auth

# Load environment variables
load_dotenv()

def create_dummy_users(db: Session) -> list[User]:
    """Create dummy users with hashed passwords"""
    print("Creating dummy users...")
    
    dummy_users_data = [
        {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "bio": "Tech enthusiast and event organizer",
            "avatar_url": "https://example.com/avatars/john.jpg"
        },
        {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "password": "password123",
            "bio": "Community manager and social butterfly",
            "avatar_url": "https://example.com/avatars/jane.jpg"
        },
        {
            "name": "Mike Johnson",
            "email": "mike.johnson@example.com",
            "password": "password123",
            "bio": "Developer and meetup enthusiast",
            "avatar_url": "https://example.com/avatars/mike.jpg"
        },
        {
            "name": "Sarah Wilson",
            "email": "sarah.wilson@example.com",
            "password": "password123",
            "bio": "Designer and creative event planner",
            "avatar_url": "https://example.com/avatars/sarah.jpg"
        },
        {
            "name": "David Brown",
            "email": "david.brown@example.com",
            "password": "password123",
            "bio": "Entrepreneur and networking expert",
            "avatar_url": "https://example.com/avatars/david.jpg"
        },
        {
            "name": "Lisa Davis",
            "email": "lisa.davis@example.com",
            "password": "password123",
            "bio": "Marketing professional and community builder",
            "avatar_url": "https://example.com/avatars/lisa.jpg"
        },
        {
            "name": "Tom Anderson",
            "email": "tom.anderson@example.com",
            "password": "password123",
            "bio": "Student and aspiring developer",
            "avatar_url": "https://example.com/avatars/tom.jpg"
        },
        {
            "name": "Emma Taylor",
            "email": "emma.taylor@example.com",
            "password": "password123",
            "bio": "Product manager and team leader",
            "avatar_url": "https://example.com/avatars/emma.jpg"
        }
    ]
    
    users = []
    for user_data in dummy_users_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"User {user_data['email']} already exists, skipping...")
            users.append(existing_user)
            continue
            
        # Hash the password
        hashed_password = auth.get_password_hash(user_data["password"])
        
        # Create user
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            password_hash=hashed_password,
            bio=user_data["bio"],
            avatar_url=user_data["avatar_url"],
            is_active=1
        )
        
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"Created {len(users)} users")
    return users

def create_dummy_groups(db: Session, users: list[User]) -> list[Group]:
    """Create dummy groups with different owners"""
    print("Creating dummy groups...")
    
    dummy_groups_data = [
        {
            "name": "Tech Enthusiasts",
            "description": "A community for technology lovers to share ideas and organize tech events",
            "avatar_url": "https://example.com/groups/tech.jpg"
        },
        {
            "name": "Startup Founders",
            "description": "Network of entrepreneurs and startup founders sharing experiences",
            "avatar_url": "https://example.com/groups/startup.jpg"
        },
        {
            "name": "Design Community",
            "description": "Creative minds coming together to discuss design trends and techniques",
            "avatar_url": "https://example.com/groups/design.jpg"
        },
        {
            "name": "Data Science Meetup",
            "description": "Data scientists and analysts sharing knowledge and projects",
            "avatar_url": "https://example.com/groups/datascience.jpg"
        },
        {
            "name": "Marketing Professionals",
            "description": "Marketing experts discussing strategies and industry trends",
            "avatar_url": "https://example.com/groups/marketing.jpg"
        }
    ]
    
    groups = []
    for i, group_data in enumerate(dummy_groups_data):
        # Check if group already exists
        existing_group = db.query(Group).filter(Group.name == group_data["name"]).first()
        if existing_group:
            print(f"Group {group_data['name']} already exists, skipping...")
            groups.append(existing_group)
            continue
            
        # Assign different owners
        owner = users[i % len(users)]
        
        group = Group(
            name=group_data["name"],
            description=group_data["description"],
            avatar_url=group_data["avatar_url"],
            owner_id=owner.id
        )
        
        db.add(group)
        groups.append(group)
    
    db.commit()
    print(f"Created {len(groups)} groups")
    return groups

def create_dummy_group_members(db: Session, users: list[User], groups: list[Group]):
    """Create group memberships"""
    print("Creating group memberships...")
    
    # Create memberships for each group
    memberships_created = 0
    for group in groups:
        # Add the owner as a member (if not already)
        existing_owner_membership = db.query(GroupMember).filter(
            GroupMember.group_id == group.id,
            GroupMember.user_id == group.owner_id
        ).first()
        
        if not existing_owner_membership:
            owner_membership = GroupMember(
                group_id=group.id,
                user_id=group.owner_id
            )
            db.add(owner_membership)
            memberships_created += 1
        
        # Add 3-5 random members to each group
        import random
        other_users = [u for u in users if u.id != group.owner_id]
        num_members = random.randint(3, min(5, len(other_users)))
        selected_users = random.sample(other_users, num_members)
        
        for user in selected_users:
            # Check if membership already exists
            existing_membership = db.query(GroupMember).filter(
                GroupMember.group_id == group.id,
                GroupMember.user_id == user.id
            ).first()
            
            if not existing_membership:
                membership = GroupMember(
                    group_id=group.id,
                    user_id=user.id
                )
                db.add(membership)
                memberships_created += 1
    
    db.commit()
    print(f"Created {memberships_created} group memberships")

def create_dummy_events(db: Session, users: list[User]) -> list[Event]:
    """Create dummy events with different organizers"""
    print("Creating dummy events...")
    
    # Generate events for the next 30 days
    base_date = datetime.now().date()
    
    dummy_events_data = [
        {
            "title": "Python Web Development Workshop",
            "description": "Learn how to build web applications with Python and FastAPI",
            "location": "Tech Hub, 123 Main St, San Francisco, CA",
            "banner_url": "https://example.com/events/python-workshop.jpg"
        },
        {
            "title": "Startup Pitch Night",
            "description": "Watch amazing startups pitch their ideas to investors",
            "location": "Innovation Center, 456 Startup Ave, Palo Alto, CA",
            "banner_url": "https://example.com/events/pitch-night.jpg"
        },
        {
            "title": "UI/UX Design Meetup",
            "description": "Discuss the latest trends in user interface and experience design",
            "location": "Design Studio, 789 Creative Blvd, San Francisco, CA",
            "banner_url": "https://example.com/events/design-meetup.jpg"
        },
        {
            "title": "Data Science Conference 2024",
            "description": "Annual conference featuring talks on machine learning and AI",
            "location": "Convention Center, 321 Data Dr, San Jose, CA",
            "banner_url": "https://example.com/events/datascience-conf.jpg"
        },
        {
            "title": "Marketing Strategy Workshop",
            "description": "Learn effective marketing strategies for digital businesses",
            "location": "Business Center, 654 Marketing St, Oakland, CA",
            "banner_url": "https://example.com/events/marketing-workshop.jpg"
        },
        {
            "title": "Networking Happy Hour",
            "description": "Casual networking event for professionals in tech",
            "location": "The Tech Bar, 987 Social Ave, San Francisco, CA",
            "banner_url": "https://example.com/events/networking.jpg"
        },
        {
            "title": "Mobile App Development Bootcamp",
            "description": "Intensive bootcamp on mobile app development",
            "location": "Code Academy, 147 Learning St, Berkeley, CA",
            "banner_url": "https://example.com/events/mobile-bootcamp.jpg"
        },
        {
            "title": "Product Management Summit",
            "description": "Learn from top product managers in the industry",
            "location": "Product Hub, 258 PM Ave, San Francisco, CA",
            "banner_url": "https://example.com/events/pm-summit.jpg"
        }
    ]
    
    events = []
    for i, event_data in enumerate(dummy_events_data):
        # Check if event already exists
        existing_event = db.query(Event).filter(Event.title == event_data["title"]).first()
        if existing_event:
            print(f"Event {event_data['title']} already exists, skipping...")
            events.append(existing_event)
            continue
            
        # Assign different organizers
        organizer = users[i % len(users)]
        
        # Generate event date (spread over next 30 days)
        event_date = base_date + timedelta(days=i * 4)
        event_time = time(18, 0, 0)  # 6:00 PM
        
        event = Event(
            title=event_data["title"],
            description=event_data["description"],
            date=event_date,
            time=event_time.strftime("%H:%M:%S"),
            location=event_data["location"],
            organizer_id=organizer.id,
            banner_url=event_data["banner_url"]
        )
        
        db.add(event)
        events.append(event)
    
    db.commit()
    print(f"Created {len(events)} events")
    return events

def create_dummy_rsvps(db: Session, users: list[User], events: list[Event]):
    """Create dummy RSVPs with various statuses"""
    print("Creating dummy RSVPs...")
    
    import random
    
    rsvp_statuses = ["yes", "no", "maybe"]
    rsvps_created = 0
    
    for event in events:
        # Each event should have 5-8 RSVPs
        num_rsvps = random.randint(5, min(8, len(users)))
        selected_users = random.sample(users, num_rsvps)
        
        for user in selected_users:
            # Check if RSVP already exists
            existing_rsvp = db.query(RSVP).filter(
                RSVP.event_id == event.id,
                RSVP.user_id == user.id
            ).first()
            
            if not existing_rsvp:
                status = random.choice(rsvp_statuses)
                rsvp = RSVP(
                    user_id=user.id,
                    event_id=event.id,
                    status=status
                )
                db.add(rsvp)
                rsvps_created += 1
    
    db.commit()
    print(f"Created {rsvps_created} RSVPs")

def clear_existing_data(db: Session):
    """Clear existing data (optional - uncomment if needed)"""
    print("Clearing existing data...")
    
    # Delete in reverse order of dependencies
    db.query(RSVP).delete()
    db.query(Event).delete()
    db.query(GroupMember).delete()
    db.query(Group).delete()
    db.query(User).delete()
    
    db.commit()
    print("Existing data cleared")

def main():
    """Main function to run the dummy data insertion"""
    print("Starting dummy data insertion...")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Uncomment the line below if you want to clear existing data
        # clear_existing_data(db)
        
        # Create dummy data
        users = create_dummy_users(db)
        groups = create_dummy_groups(db, users)
        create_dummy_group_members(db, users, groups)
        events = create_dummy_events(db, users)
        create_dummy_rsvps(db, users, events)
        
        print("=" * 50)
        print("Dummy data insertion completed successfully!")
        print(f"Summary:")
        print(f"- Users: {len(users)}")
        print(f"- Groups: {len(groups)}")
        print(f"- Events: {len(events)}")
        print(f"- Group memberships and RSVPs created")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
 john.doe@example.com (password: password123)
📧 jane.smith@example.com (password: password123)
📧 mike.johnson@example.com (password: password123)
📧 sarah.wilson@example.com (password: password123)
📧 david.brown@example.com (password: password123)
📧 lisa.davis@example.com (password: password123)
📧 tom.anderson@example.com (password: password123)
📧 emma.taylor@example.com (password: password123)
