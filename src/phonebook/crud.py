from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import Computer, utcnow_iso

# Fields that CRUD reads from incoming data, in persistence order.
_FIELDS = (
    "friendly_name",
    "rustdesk_id",
    "hostname",
    "local_ip",
    "operating_system",
    "username",
    "location",
    "notes",
    "tags",
)


def _as_dict(data) -> dict:
    """Accept a validated Pydantic schema (the route path) or a plain dict."""
    if isinstance(data, dict):
        return dict(data)
    if hasattr(data, "model_dump"):  # pydantic v2
        return data.model_dump()
    if hasattr(data, "dict"):  # pydantic v1
        return data.dict()
    raise TypeError(f"Unsupported data type for CRUD: {type(data)!r}")


def _clean(value):
    """Strip surrounding whitespace from string values; leave others untouched."""
    return value.strip() if isinstance(value, str) else value


def get_all_computers(db: Session) -> list[Computer]:
    """Query all Computer objects, ordered by friendly_name ascending."""
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
            Computer.notes.ilike(f"%{q}%"),
        )
    ).all()


def create_computer(db: Session, data) -> Computer:
    """Create a new Computer from validated schema data (or a dict)."""
    d = _as_dict(data)
    now = utcnow_iso()
    computer = Computer(
        **{field: _clean(d.get(field)) for field in _FIELDS},
        created_at=now,
        updated_at=now,
    )

    db.add(computer)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(computer)
    return computer


def update_computer(db: Session, computer_id: int, data) -> Computer | None:
    """Update a Computer with provided values, skipping fields left as None."""
    computer = get_computer(db, computer_id)
    if not computer:
        return None

    d = _as_dict(data)
    for field in _FIELDS:
        if field in d and d[field] is not None:
            setattr(computer, field, _clean(d[field]))

    computer.updated_at = utcnow_iso()

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(computer)
    return computer


def delete_computer(db: Session, computer_id: int) -> bool:
    """Delete a Computer by id. Returns True if a row was removed."""
    computer = get_computer(db, computer_id)
    if not computer:
        return False

    db.delete(computer)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
