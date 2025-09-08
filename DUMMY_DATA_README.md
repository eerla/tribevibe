# Dummy Data Insertion Script

This directory contains scripts to populate your TribeVibe database with comprehensive dummy data for testing all APIs.

## Files

- `insert_dummy_data.py` - Main script that creates dummy data
- `run_dummy_data.py` - Simple runner script with user-friendly output
- `DUMMY_DATA_README.md` - This documentation file

## What Data is Created

The script creates the following dummy data:

### 👥 Users (8 users)
- John Doe (john.doe@example.com)
- Jane Smith (jane.smith@example.com)
- Mike Johnson (mike.johnson@example.com)
- Sarah Wilson (sarah.wilson@example.com)
- David Brown (david.brown@example.com)
- Lisa Davis (lisa.davis@example.com)
- Tom Anderson (tom.anderson@example.com)
- Emma Taylor (emma.taylor@example.com)

**Password for all users:** `password123`

### 🏢 Groups (5 groups)
- Tech Enthusiasts
- Startup Founders
- Design Community
- Data Science Meetup
- Marketing Professionals

### 👥 Group Memberships
- Each group has 3-5 members (including the owner)
- Members are randomly assigned from the user pool

### 📅 Events (8 events)
- Python Web Development Workshop
- Startup Pitch Night
- UI/UX Design Meetup
- Data Science Conference 2024
- Marketing Strategy Workshop
- Networking Happy Hour
- Mobile App Development Bootcamp
- Product Management Summit

### ✅ RSVPs
- Each event has 5-8 RSVPs
- RSVP statuses: "yes", "no", "maybe"
- Randomly assigned to users

## Prerequisites

1. **Database Setup**: Make sure your database is running and accessible
2. **Environment Variables**: Ensure your `.env` file is configured with:
   - `DATABASE_URL`
   - `SECRET_KEY` (for JWT tokens)
   - Any other required environment variables

3. **Dependencies**: Install all required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Option 1: Using the runner script (Recommended)
```bash
python run_dummy_data.py
```

### Option 2: Running the main script directly
```bash
python insert_dummy_data.py
```

## Features

- **Idempotent**: Safe to run multiple times - won't create duplicates
- **Comprehensive**: Covers all API endpoints in your project
- **Realistic Data**: Uses realistic names, emails, and descriptions
- **Proper Relationships**: Creates proper foreign key relationships
- **Password Hashing**: Uses the same password hashing as your auth system

## API Endpoints Covered

### User APIs (`/users`)
- ✅ User registration
- ✅ User login
- ✅ Get current user profile

### Group APIs (`/groups`)
- ✅ Create group
- ✅ Join group
- ✅ Get user's groups
- ✅ Get all groups
- ✅ Get group details
- ✅ Get group members

### Event APIs (`/events`)
- ✅ Create event
- ✅ List all events
- ✅ Get event details
- ✅ RSVP to event
- ✅ Cancel RSVP
- ✅ Get user's registrations
- ✅ Get event RSVPs
- ✅ Upload event banner

## Testing Your APIs

After running the script, you can test your APIs using the created users:

1. **Login** with any of the test users:
   ```bash
   curl -X POST "http://localhost:8000/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=john.doe@example.com&password=password123"
   ```

2. **Use the returned token** for authenticated requests:
   ```bash
   curl -X GET "http://localhost:8000/events/" \
        -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

## Clearing Data (Optional)

If you need to clear existing data before inserting dummy data, uncomment the `clear_existing_data(db)` line in the `main()` function of `insert_dummy_data.py`.

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check your `DATABASE_URL` in `.env`
   - Ensure your database is running

2. **Import Errors**
   - Make sure you're running the script from the project root directory
   - Check that all dependencies are installed

3. **Permission Errors**
   - Ensure the script has write permissions to the database
   - Check database user permissions

### Getting Help

If you encounter issues:
1. Check the console output for specific error messages
2. Verify your database connection
3. Ensure all environment variables are set correctly
4. Check that all required dependencies are installed

## Customization

You can easily customize the dummy data by modifying the data arrays in `insert_dummy_data.py`:

- `dummy_users_data` - Add/modify user data
- `dummy_groups_data` - Add/modify group data
- `dummy_events_data` - Add/modify event data

The script will automatically handle relationships and avoid duplicates.
