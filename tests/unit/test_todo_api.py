import pytest
from datetime import datetime, UTC
from models.todo import Todo


def test_list_todo_empty(client):
    """Test listing todos when database is empty."""
    response = client.get("/api/v1/todo")
    assert response.status_code == 200
    assert response.json() == []


def test_list_todo_with_pagination(client, db_session):
    """Test listing todos with pagination."""
    # Create 15 test todos
    for i in range(15):
        todo = Todo(task=f"Task {i}")
        db_session.add(todo)
    db_session.commit()

    # Test first page
    response = client.get("/api/v1/todo?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

    # Test second page
    response = client.get("/api/v1/todo?page=2&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


def test_create_todo_with_all_fields(client):
    """Test creating a todo with all fields."""
    todo_data = {
        "task": "Buy groceries",
        "due_date": "2025-12-31T23:59:59Z"
    }
    response = client.post("/api/v1/todo", json=todo_data)
    assert response.status_code == 200

    data = response.json()
    assert data["task"] == "Buy groceries"
    assert data["due_date"] is not None
    assert "id" in data
    assert "create_date" in data
    assert "update_date" in data


def test_create_todo_minimal_fields(client):
    """Test creating a todo with only required fields."""
    todo_data = {
        "task": "Call dentist"
    }
    response = client.post("/api/v1/todo", json=todo_data)
    assert response.status_code == 200

    data = response.json()
    assert data["task"] == "Call dentist"
    assert data["due_date"] is None
    assert "id" in data


def test_create_todo_missing_required_field(client):
    """Test creating a todo without required field."""
    todo_data = {
        "due_date": "2025-12-31T23:59:59Z"
    }
    response = client.post("/api/v1/todo", json=todo_data)
    assert response.status_code == 422  # Validation error


def test_get_todo_by_id(client, db_session):
    """Test retrieving a todo by ID."""
    todo = Todo(task="Test task", due_date=datetime(2025, 12, 31, tzinfo=UTC))
    db_session.add(todo)
    db_session.commit()
    todo_id = todo.id

    response = client.get(f"/api/v1/todo/{todo_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == todo_id
    assert data["task"] == "Test task"
    assert data["due_date"] is not None


def test_get_todo_by_id_not_found(client):
    """Test retrieving a non-existent todo."""
    response = client.get("/api/v1/todo/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_todo_full(client, db_session):
    """Test full update of a todo (PUT)."""
    todo = Todo(task="Original task")
    db_session.add(todo)
    db_session.commit()
    todo_id = todo.id

    updated_data = {
        "task": "Updated task",
        "due_date": "2025-12-31T23:59:59Z"
    }
    response = client.put(f"/api/v1/todo/{todo_id}", json=updated_data)
    assert response.status_code == 200

    data = response.json()
    assert data["task"] == "Updated task"
    assert data["due_date"] is not None


def test_update_todo_partial(client, db_session):
    """Test partial update of a todo (PATCH)."""
    todo = Todo(task="Original task", due_date=datetime(2025, 12, 31, tzinfo=UTC))
    db_session.add(todo)
    db_session.commit()
    todo_id = todo.id

    # Only update task
    updated_data = {
        "task": "Partially updated task"
    }
    response = client.patch(f"/api/v1/todo/{todo_id}", json=updated_data)
    assert response.status_code == 200

    data = response.json()
    assert data["task"] == "Partially updated task"
    assert data["due_date"] is not None  # Should remain unchanged


def test_update_todo_not_found(client):
    """Test updating a non-existent todo."""
    updated_data = {
        "task": "Updated task"
    }
    response = client.put("/api/v1/todo/99999", json=updated_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_todo(client, db_session):
    """Test deleting a todo."""
    todo = Todo(task="Task to delete")
    db_session.add(todo)
    db_session.commit()
    todo_id = todo.id

    response = client.delete(f"/api/v1/todo/{todo_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["detail"]

    # Verify it's actually deleted
    assert db_session.query(Todo).filter(Todo.id == todo_id).first() is None


def test_delete_todo_not_found(client):
    """Test deleting a non-existent todo."""
    response = client.delete("/api/v1/todo/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_todo_timestamps(client, db_session):
    """Test that create_date and update_date are set correctly."""
    # Create a todo
    todo_data = {"task": "Test timestamps"}
    response = client.post("/api/v1/todo", json=todo_data)
    assert response.status_code == 200

    data = response.json()
    todo_id = data["id"]
    create_date = data["create_date"]
    update_date = data["update_date"]

    assert create_date is not None
    assert update_date is not None

    # Update the todo
    updated_data = {"task": "Updated timestamps"}
    response = client.patch(f"/api/v1/todo/{todo_id}", json=updated_data)
    assert response.status_code == 200

    updated = response.json()
    assert updated["create_date"] == create_date  # Should not change
    assert updated["update_date"] >= update_date  # Should be updated
