# Group API Documentation

## Overview
The Group API provides endpoints for creating, managing, and interacting with groups in the TribeVibe application.

## Base URL
```
http://127.0.0.1:8000/groups
```

## Authentication
Most endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Create a Group
**POST** `/groups/`

Creates a new group. The authenticated user becomes the owner and first member.

**Request Body:**
```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "avatar_url": "string (optional)"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "My Group",
  "description": "A great group",
  "owner_id": 123,
  "created_at": "2024-01-01T12:00:00Z",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

**Status Codes:**
- `200`: Group created successfully
- `400`: Group name already exists
- `401`: Authentication required

### 2. Get All Groups
**GET** `/groups/`

Retrieves all groups in the system.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Group 1",
    "description": "Description 1",
    "owner_id": 123,
    "created_at": "2024-01-01T12:00:00Z",
    "avatar_url": null
  }
]
```

### 3. Get Group by ID
**GET** `/groups/{group_id}`

Retrieves a specific group by its ID.

**Parameters:**
- `group_id` (path): The ID of the group

**Response:**
```json
{
  "id": 1,
  "name": "My Group",
  "description": "A great group",
  "owner_id": 123,
  "created_at": "2024-01-01T12:00:00Z",
  "avatar_url": null
}
```

**Status Codes:**
- `200`: Group found
- `404`: Group not found

### 4. Join a Group
**POST** `/groups/{group_id}/join`

Allows the authenticated user to join a group.

**Parameters:**
- `group_id` (path): The ID of the group to join

**Response:**
```json
{
  "id": 1,
  "group_id": 1,
  "user_id": 123,
  "joined_at": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200`: Successfully joined group
- `400`: Already a member
- `401`: Authentication required
- `404`: Group not found

### 5. Get My Groups
**GET** `/groups/my-groups`

Retrieves all groups that the authenticated user is a member of.

**Response:**
```json
[
  {
    "id": 1,
    "name": "My Group",
    "description": "A great group",
    "owner_id": 123,
    "created_at": "2024-01-01T12:00:00Z",
    "avatar_url": null
  }
]
```

**Status Codes:**
- `200`: Success
- `401`: Authentication required

### 6. Get Group Members
**GET** `/groups/{group_id}/members`

Retrieves all members of a specific group.

**Parameters:**
- `group_id` (path): The ID of the group

**Response:**
```json
[
  {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

## Example Usage

### Creating a Group
```bash
curl -X POST "http://127.0.0.1:8000/groups/" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Photography Enthusiasts",
    "description": "A group for photography lovers to share tips and organize photo walks",
    "avatar_url": "https://example.com/photography-group-avatar.jpg"
  }'
```

### Joining a Group
```bash
curl -X POST "http://127.0.0.1:8000/groups/1/join" \
  -H "Authorization: Bearer <your_jwt_token>"
```

### Getting All Groups
```bash
curl -X GET "http://127.0.0.1:8000/groups/"
```

## Database Schema

### Groups Table
- `id`: Primary key
- `name`: Unique group name
- `description`: Optional group description
- `owner_id`: Foreign key to users table
- `created_at`: Timestamp when group was created
- `avatar_url`: Optional URL for group avatar

### Group Members Table
- `id`: Primary key
- `group_id`: Foreign key to groups table
- `user_id`: Foreign key to users table
- `joined_at`: Timestamp when user joined the group

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid input or business logic error
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a `detail` field with a description of the error.

