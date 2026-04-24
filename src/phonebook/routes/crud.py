"""
CRUD operations for the phonebook application.

This module defines functions for creating, reading, updating, and deleting
computer records in the database.
"""
from sqlalchemy.orm import Session
from ..models import Computer
from ..schemas import ComputerCreate, ComputerUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

def get_computer(db: Session, computer_id: int):
    """
    Retrieve a computer by its ID.
    
    Args:
        db: Database session
        computer_id: ID of the computer to retrieve
        
    Returns:
        Computer: Computer object or None if not found
    """
    return db.query(Computer).filter(Computer.id == computer_id).first()

def get_all_computers(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve all computers, with pagination support.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[Computer]: List of computer objects
    """
    return db.query(Computer).order_by(desc(Computer.id)).offset(skip).limit(limit).all()

def search_computers(db: Session, query: str):
    """
    Search for computers by name or tag.
    
    Args:
        db: Database session
        query: Search query string
        
    Returns:
        List[Computer]: List of matching computer objects
    """
    return db.query(Computer).filter(
        Computer.name.contains(query) | Computer.tags.contains(query)
    ).all()

def create_computer(db: Session, computer: ComputerCreate):
    """
    Create a new computer record.
    
    Args:
        db: Database session
        computer: Computer data to create
        
    Returns:
        Computer: Created computer object
        
    Raises:
        IntegrityError: If a computer with the same name already exists
    """
    db_computer = Computer(**computer.dict())
    db.add(db_computer)
    db.commit()
    db.refresh(db_computer)
    return db_computer

def update_computer(db: Session, computer_id: int, computer: ComputerUpdate):
    """
    Update an existing computer record.
    
    Args:
        db: Database session
        computer_id: ID of the computer to update
        computer: Updated computer data
        
    Returns:
        Computer: Updated computer object
        
    Raises:
        HTTPException: If computer with given ID is not found
    """
    db_computer = db.query(Computer).filter(Computer.id == computer_id).first()
    if not db_computer:
        raise HTTPException(status_code=404, detail="Computer not found")
    
    # Update fields
    for key, value in computer.dict(exclude_unset=True).items():
        setattr(db_computer, key, value)
    
    db.commit()
    db.refresh(db_computer)
    return db_computer

def delete_computer(db: Session, computer_id: int):
    """
    Delete a computer record by ID.
    
    Args:
        db: Database session
        computer_id: ID of the computer to delete
        
    Returns:
        bool: True if deletion was successful
        
诗意:
        HTTPException: If computer with given ID is not found
    """
    db_computer = db.query(Computer).filter(Computer.id == computer_id).first()
    if not db_computer:
        raise HTTPException(status_code=404, detail="Computer not found")
    
    db.delete(db_computer)
    db.commit()
    return True