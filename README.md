# meetup_clone_backend

## Events API

### GET /events

Get a list of events with optional filtering capabilities.

**Query Parameters:**
- `city` (optional): Filter events by city (searches in location field)
- `category` (optional): Filter events by category
- `date` (optional): Filter events by specific date (format: YYYY-MM-DD)

**Examples:**
```bash
# Get all events
GET /events

# Get events in San Francisco
GET /events?city=San Francisco

# Get Technology events
GET /events?category=Technology

# Get events on a specific date
GET /events?date=2024-01-15

# Combine multiple filters
GET /events?city=New York&category=Music&date=2024-01-15
```

**Response:**
Returns an array of event objects with the following structure:
```json
[
  {
    "id": 1,
    "title": "Tech Meetup",
    "description": "A great tech meetup",
    "date": "2024-01-15",
    "time": "18:00:00",
    "location": "San Francisco, CA",
    "category": "Technology",
    "organizer": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "created_at": "2024-01-01T00:00:00"
    },
    "created_at": "2024-01-01T00:00:00",
    "banner_url": "https://example.com/banner.jpg",
    "rsvp_count": 25,
    "rsvp_status": "yes"
  }
]
```

## Organizer Endpoints

### GET /events/organizers/me/events

Get all events created by the current user (organizer).

**Authentication Required:** Yes (Bearer token)

**Response:**
Returns an array of event objects created by the current user, ordered by date.

**Example:**
```bash
GET /events/organizers/me/events
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "My Tech Meetup",
    "description": "A great tech meetup I organized",
    "date": "2024-01-15",
    "time": "18:00:00",
    "location": "San Francisco, CA",
    "category": "Technology",
    "organizer": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "created_at": "2024-01-01T00:00:00"
    },
    "created_at": "2024-01-01T00:00:00",
    "banner_url": "https://example.com/banner.jpg",
    "rsvp_count": 25,
    "rsvp_status": "yes"
  }
]
```

### GET /events/organizers/{organizer_id}

Get organizer profile by ID.

**Authentication Required:** No

**Path Parameters:**
- `organizer_id` (integer): The ID of the organizer

**Response:**
Returns the organizer's basic profile information.

**Example:**
```bash
GET /events/organizers/123
```

**Response:**
```json
{
  "id": 123,
  "name": "Jane Smith",
  "email": "jane@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

**Error Responses:**
- `400`: Invalid organizer ID
- `404`: Organizer not found
- `500`: Server error

### PUT /events/{event_id}

Update an existing event. Only the event organizer can update their event.

**Authentication Required:** Yes (Bearer token)

**Path Parameters:**
- `event_id` (integer): The ID of the event to update

**Request Body:**
All fields are optional - only provided fields will be updated.
```json
{
  "title": "Updated Event Title",
  "description": "Updated event description",
  "date": "2024-01-20",
  "time": "19:00:00",
  "location": "New Location, City",
  "category": "Updated Category"
}
```

**Field Formats:**
- `date`: String in `"YYYY-MM-DD"` format (e.g., `"2024-02-01"`)
- `time`: String in either:
  - Standard format: `"19:00:00"` (HH:MM:SS)
  - ISO format: `"2025-09-08T02:01:44.542Z"` (will be converted to HH:MM:SS)

**Response:**
Returns the updated event object with the same structure as the GET /events response.

**Examples:**
```bash
# Update event title and description
PUT /events/1
{
  "title": "New Event Title",
  "description": "Updated description"
}

# Update event date and time
PUT /events/1
{
  "date": "2024-02-01",
  "time": "20:00:00"
}

# Update event location and category
PUT /events/1
{
  "location": "New Venue, San Francisco",
  "category": "Technology"
}
```

**Validation Rules:**
- `title`: Required if provided, max 200 characters, cannot be empty
- `description`: Optional, max 2000 characters
- `date`: Must be in YYYY-MM-DD format, cannot be in the past
- `time`: Must be in HH:MM:SS format or ISO format, cannot be empty
- `location`: Required if provided, max 500 characters, cannot be empty
- `category`: Optional, max 100 characters

**Error Responses:**
- `400`: Invalid request data, validation errors, or no fields provided
  ```json
  {
    "detail": "Validation error for field 'date': Event date cannot be in the past"
  }
  ```
- `401`: Authentication required
- `403`: Not authorized to update this event (only organizer can update)
- `404`: Event not found
- `500`: Database or server errors
  ```json
  {
    "detail": "Database error while saving changes. Please try again."
  }
  ```