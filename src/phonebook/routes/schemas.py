"""
Data schemas for the phonebook application.
"""
from pydantic import BaseModel
from typing import Optional, List

from phonebook.models import Computer

class ComputerBase(BaseModel):
    """
    Base schema for Computer model.
    """
    friendly_name: Optional[str] = None
    hostname: Optional[str] = None
    local_ip: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    operating_system: Optional[str] = None
    rustdesk_id: Optional[str] = None
    tags: Optional[List[str]] = None
    username: Optional[str] = None

class ComputerCreate(ComputerBase):
    """
    Schema for creating a new computer.
    """
    pass

class ComputerUpdate(ComputerBase):
    """
    Schema for updating an existing computer.
    """
    pass

class ComputerOut(ComputerBase):
    """
    Schema for returning computer data.
    """
    id: int
    created_at: str
    updated_at: str

    class Config:
        """
        Configuration for ComputerOut schema.
        """
        from_attributes = True

def casual_greeting() -> str:
    """
    Return a casual greeting.
    
    Returns:
        str: Casual greeting message
    """
    return "Hey"
