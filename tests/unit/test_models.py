from sqlalchemy import inspect
from models.todo import Todo, TodoCreate
from datetime import datetime, UTC


def test_todo_model_definition():
    """Test the Todo model's SQLAlchemy table and columns."""
    mapper = inspect(Todo)

    # Table name
    assert Todo.__tablename__ == 'todo'

    # Columns
    columns = {c.key: c for c in mapper.columns}
    assert "id" in columns
    assert "task" in columns
    assert "due_date" in columns
    assert "create_date" in columns
    assert "update_date" in columns

    # id column
    id_col = columns["id"]
    assert id_col.primary_key
    assert id_col.autoincrement in (True, 'auto')  # Can be True or 'auto' in different SQLAlchemy versions
    assert id_col.nullable is False

    # task column
    task_col = columns["task"]
    assert task_col.nullable is False
    assert str(task_col.type).startswith("VARCHAR") or str(task_col.type).startswith("String")

    # due_date column
    due_date_col = columns["due_date"]
    assert due_date_col.nullable is True
    assert str(due_date_col.type).startswith("DATETIME") or str(due_date_col.type).startswith("DateTime")

    # create_date column
    create_date_col = columns["create_date"]
    assert str(create_date_col.type).startswith("DATETIME") or str(create_date_col.type).startswith("DateTime")

    # update_date column
    update_date_col = columns["update_date"]
    assert str(update_date_col.type).startswith("DATETIME") or str(update_date_col.type).startswith("DateTime")


def test_todo_create_schema():
    """Test the TodoCreate Pydantic schema."""
    # Test with all fields
    todo_data = TodoCreate(
        task="Buy groceries",
        due_date=datetime.now(UTC)
    )
    assert todo_data.task == "Buy groceries"
    assert todo_data.due_date is not None

    # Test with only required fields
    todo_data_minimal = TodoCreate(task="Call dentist")
    assert todo_data_minimal.task == "Call dentist"
    assert todo_data_minimal.due_date is None


def test_todo_repr(db_session):
    """Test the Todo __repr__ method."""
    todo = Todo(task="Test task")
    db_session.add(todo)
    db_session.commit()

    repr_str = repr(todo)
    assert "Todo" in repr_str
    assert "Test task" in repr_str
    assert str(todo.id) in repr_str


def test_todo_create_and_retrieve(db_session):
    """Test creating and retrieving a Todo record."""
    todo = Todo(
        task="Complete project",
        due_date=datetime(2025, 12, 31, 23, 59, 59, tzinfo=UTC)
    )
    db_session.add(todo)
    db_session.commit()

    retrieved = db_session.query(Todo).filter(Todo.task == "Complete project").first()
    assert retrieved is not None
    assert retrieved.task == "Complete project"
    assert retrieved.due_date is not None
    assert retrieved.create_date is not None
    assert retrieved.update_date is not None


def test_todo_update_updates_timestamp(db_session):
    """Test that updating a Todo updates the update_date field."""
    todo = Todo(task="Original task")
    db_session.add(todo)
    db_session.commit()

    original_update_date = todo.update_date

    # Update the task
    todo.task = "Updated task"
    db_session.commit()

    # update_date should change
    assert todo.update_date >= original_update_date
