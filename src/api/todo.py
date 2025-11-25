from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from framework.db import get_db
from models.todo import Todo, TodoCreate
from datetime import datetime, UTC

router = APIRouter()

def serialize_sqlalchemy_obj(obj):
    """
    Convert a SQLAlchemy ORM model instance into a dictionary.

    Args:
        obj: SQLAlchemy model instance.

    Returns:
        dict: Dictionary containing all column names and their values.
    """
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


@router.get("/api/v1/todo")
def list_todo(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a paginated list of Todo records.

    Args:
        page (int): Page number starting from 1.
        limit (int): Maximum number of records to return per page.
        db (Session): SQLAlchemy database session.

    Returns:
        list[dict]: A list of serialized Todo records.
    """
    try:
        offset = (page - 1) * limit
        todo_records = db.query(Todo).offset(offset).limit(limit).all()
        return [serialize_sqlalchemy_obj(item) for item in todo_records]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/api/v1/todo")
def create_record(
    todo_data: TodoCreate = Body(..., description="Data for the new record"),
    db: Session = Depends(get_db)
):
    """
    Create a new Todo record.

    Args:
        todo_data (TodoCreate): Data model for the record to create.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The newly created Todo record.
    """
    try:
        data = todo_data.model_dump(exclude_unset=True)
        new_record = Todo(**data)
        new_record.create_date = datetime.now(UTC)
        new_record.update_date = datetime.now(UTC)

        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return serialize_sqlalchemy_obj(new_record)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/api/v1/todo/{id}")
def get_todo_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single Todo record by ID.

    Args:
        id (int): The ID of the record.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The matching Todo record.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(Todo).filter(Todo.id == id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"Todo with id {id} not found")
        return serialize_sqlalchemy_obj(record)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/api/v1/todo/{id}")
def update_todo_full(
    id: int,
    todo_data: TodoCreate = Body(..., description="Updated data for the record"),
    db: Session = Depends(get_db)
):
    """
    Fully update an existing Todo record (all fields required).

    Args:
        id (int): The ID of the record to update.
        todo_data (TodoCreate): Updated record data (all fields).
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The updated Todo record.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(Todo).filter(Todo.id == id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"Todo with id {id} not found")

        data = todo_data.model_dump(exclude_unset=False)
        for key, value in data.items():
            setattr(record, key, value)

        record.update_date = datetime.now(UTC)
        db.commit()
        db.refresh(record)
        return serialize_sqlalchemy_obj(record)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/api/v1/todo/{id}")
def update_todo_partial(
    id: int,
    todo_data: TodoCreate = Body(..., description="Partial updated data for the record"),
    db: Session = Depends(get_db)
):
    """
    Partially update an existing Todo record (only provided fields are updated).

    Args:
        id (int): The ID of the record to update.
        Todo_data (TodoCreate): Partial updated data.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: The updated Todo record.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(Todo).filter(Todo.id == id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"Todo with id {id} not found")

        data = todo_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(record, key, value)

        record.update_date = datetime.now(UTC)
        db.commit()
        db.refresh(record)
        return serialize_sqlalchemy_obj(record)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/api/v1/todo/{id}")
def delete_todo(id: int, db: Session = Depends(get_db)):
    """
    Delete a Todo record by ID.

    Args:
        id (int): The ID of the record to delete.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException: If the record is not found.
    """
    try:
        record = db.query(Todo).filter(Todo.id == id).first()
        if not record:
            raise HTTPException(status_code=404, detail=f"Todo with id {id} not found")

        db.delete(record)
        db.commit()
        return {"detail": f"Todo with id {id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
