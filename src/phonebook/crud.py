from .models import Computer
from .schemas import ComputerCreate, ComputerUpdate
from .database import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from datetime import datetime
import pytz


def get_all_computers(db: Session) -> list[Computer]:
    """Query all Computer objects from the database, ordered by friendly_name."""
    return db.query(Computer).order_by(Computer.friendly_name.asc()).all()


def get_computer(db: Session, computer_id: int) -> Computer | None:
    """Query a Computer object by its id field."""
    return db.query(Computer).filter(Computer.id == computer_id).first()


def search_computers(db: Session, q: str) -> list[Computer]:
    """Search Computer objects across multiple fields using OR logic."""
    if not q:
        raise ValueError("Search query cannot be empty")
    
    return db.query(Computer).filter(
        or_(
            Computer.friendly_name.ilike(f"%{q}%"),
            Computer.rustdesk_id.ilike(f"%{q}%"),
            Computer.hostname.ilike(f"%{q}%"),
            Computer.local_ip.ilike(f"%{q}%"),
            Computer.tags.ilike(f"%{q}%"),
            Computer.notes.ilike(f"%{q}%")
        )
    ).all()


def create_computer(db: Session, data: ComputerCreate) -> Computer:
    """Create a new Computer object with the provided data."""
    # Create the Computer object
    computer = Computer(
        friendly_name=data.friendly_name,
        rustdesk_id=data.rustdesk_id,
        hostname=data.hostname,
        local_ip=data.local_ip,
        tags=data.tags,
        notes=data.notes,
        created_at=datetime.now(pytz.UTC).isoformat(),
        updated_at=datetime.now(pytz.UTC).isoformat()
    )
    
    # Add to session and commit
    db.add(computer)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    
    # Refresh to get generated id and timestamps
    try:
        db.refresh(computer)
    except Exception:
        db.rollback()
        raise
    
    return computer


def update_computer(db: Session, computer_id: int, data: ComputerUpdate) -> Computer | None:
    """Update a Computer object with values from data, skipping None values."""
    # Retrieve the existing computer
    computer = get_computer(db, computer_id)
    if not computer:
        return None
    
    # Update fields that are not None
    if data.friendly_name is not None:
        computer.friendly_name = data.friendly_name
    if data.rustdesk_id is not None:
        computer.rustdesk_id = data.rustdesk_id
    if data.hostname is not None:
        computer.hostname = data.hostname
    if data.local_ip is not None:
        computer.local_ip = data.local_ip
    if data.tags is not None:
        computer.tags = data.tags
    if data.notes is not None:
        computer.notes = data.notes
    
    # Update timestamp
    computer.updated_at = datetime.now(pytz.UTC).isoformat()
    
    # Commit changes
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    try:
        db.refresh(computer)
    except Exception:
        db.rollback()
        raise
    
    return computer


def delete_computer(db: Session, computer_id: int) -> bool:
    """Delete a Computer object by its id."""
    # Retrieve the existing computer
    computer = get_computer(db, computer_id)
    if not computer:
        return False
    
    # Delete and commit
    db.delete(computer)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    
    return True
