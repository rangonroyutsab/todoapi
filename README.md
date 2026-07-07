# To-Do API

## Overview
This project is a lightweight, basic To-Do API built with Django REST Framework (DRF). It provides full CRUD operations for managing tasks. The API is designed with strict validation rules and uniform JSON response formatting to ensure predictability and ease of use.

## Setup Instructions
To run this project locally, ensure you have Python 3 installed.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rangonroyutsab/todoapi.git
   cd todoapi
   ```

2. **Activate the virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://127.0.0.1:8000/`.

## Endpoints Reference

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/tasks` | Retrieve a paginated, sortable, and filterable list of tasks. |
| `POST` | `/tasks` | Create a new task. |
| `GET` | `/tasks/<id>` | Retrieve a specific task by its ID. |
| `PUT` | `/tasks/<id>` | Partially update a specific task by its ID. |
| `DELETE`| `/tasks/<id>` | Delete a specific task by its ID. |

## cURL Examples

### 1. View all tasks
```bash
curl -X GET "http://127.0.0.1:8000/tasks?status=pending&page=1&limit=5&sort_by=createdAt&order=desc"
```

### 2. Create a new task
```bash
curl -X POST "http://127.0.0.1:8000/tasks" \
     -H "Content-Type: application/json" \
     -d '{"title": "Buy groceries", "description": "Milk, Eggs, Bread"}'
```

### 3. View task by ID
```bash
curl -X GET "http://127.0.0.1:8000/tasks/1"
```

### 4. Update task by ID (Partial Update)
```bash
curl -X PUT "http://127.0.0.1:8000/tasks/1" \
     -H "Content-Type: application/json" \
     -d '{"status": "done"}'
```

### 5. Delete task by ID
```bash
curl -X DELETE "http://127.0.0.1:8000/tasks/1"
```

## Response Format
The API follows a standardized response format for both successes and errors.

**Success Response:**
```json
{
  "success": true,
  "message": "Tasks retrieved successfully",
  "data": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, Eggs, Bread",
      "status": "pending",
      "createdAt": "2023-10-01T12:00:00Z",
      "updatedAt": "2023-10-01T12:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 5,
    "total": 1,
    "totalPages": 1
  }
}
```
*(Note: The `meta` block is only included in list responses).*

**Error Response:**
```json
{
  "success": false,
  "message": "Validation Error",
  "errors": {
    "title": ["This field may not be blank."]
  }
}
```

## In-Memory Storage Behavior
This API intentionally bypasses a traditional relational database (like PostgreSQL or SQLite) in favor of thread-safe in-memory storage. 

- **Volatility:** All tasks are stored in memory (`InMemoryTaskStore`) using a Python dictionary. **This means that all data is completely lost when the server is restarted.**
- **Thread Safety:** The storage mechanism utilizes Python's `threading.Lock` to ensure that concurrent read/write operations (like auto-incrementing IDs or modifying tasks) are safe and avoid race conditions.
- **Constraints:** Because there is no ORM/QuerySet, filtering, sorting, and pagination logic are handled entirely via Python lists and slices in the application layer.
