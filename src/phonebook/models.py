from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def utcnow_iso() -> str:
    """UTC timestamp as an ISO-8601 string. Timestamps are stored as TEXT."""
    return datetime.now(timezone.utc).isoformat()


class Computer(Base):
    __tablename__ = "computers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    friendly_name = Column(String, nullable=False)
    rustdesk_id = Column(String, nullable=False, unique=True)
    hostname = Column(String, nullable=True)
    local_ip = Column(String, nullable=True)
    operating_system = Column(String, nullable=True)
    username = Column(String, nullable=True)
    location = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    # Stored as TEXT (ISO-8601 strings), matching what CRUD writes.
    created_at = Column(String, nullable=False, default=utcnow_iso)
    updated_at = Column(String, nullable=False, default=utcnow_iso, onupdate=utcnow_iso)
