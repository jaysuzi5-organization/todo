"""
Todo Model and Pydantic Schema

This module defines:
- The SQLAlchemy ORM model for persisting Todo data.
- The Pydantic schema for validating API requests when creating a Todo.

"""

from sqlalchemy import Column, DateTime, Integer, String
from framework.db import Base
from datetime import datetime, UTC
from pydantic import BaseModel
from typing import Optional


class Todo(Base):
    """
    SQLAlchemy ORM model representing a Todo record.

    Attributes:
        id (int): Primary key, unique identifier for the record.
        task (str): Task description, up to 200 characters. Cannot be null.
        due_date (datetime | None): Optional due date for the task.
        create_date (datetime): Timestamp when the record was created (UTC).
        update_date (datetime): Timestamp when the record was last updated (UTC).

    Notes:
        - `create_date` is automatically set when the record is created.
        - `update_date` is automatically updated whenever the record changes.
    """

    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String(200), nullable=False, index=True)
    due_date = Column(DateTime, nullable=True)
    create_date = Column(DateTime, default=lambda: datetime.now(UTC))
    update_date = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)  # auto-update on change
    )

    def __repr__(self):
        """
        Returns a string representation of the Todo instance.

        Example:
            <Todo(id=1, task='Buy groceries')>
        """
        return f"<Todo(id={self.id}, task='{self.task}')>"


class TodoCreate(BaseModel):
    """
    Pydantic schema for creating a new Todo.

    Attributes:
        task (str): Required task description.
        due_date (datetime | None): Optional due date for the task.

    Example:
        {
            "task": "Buy groceries",
            "due_date": "2025-12-31T23:59:59Z"
        }
    """
    task: str
    due_date: Optional[datetime] = None
