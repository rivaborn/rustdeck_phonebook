from pydantic import BaseModel, Field, validator
from typing import Optional, List
import ipaddress

from phonebook.models import Computer

class ComputerCreate(BaseModel):
    friendly_name: str
    rustdesk_id: str
    hostname: Optional[str] = None
    local_ip: Optional[str] = None
    operating_system: Optional[str] = None
    username: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None

    # Validate that friendly_name is 1-120 characters, strip whitespace
    @validator("friendly_name")
    def validate_friendly_name(cls, v):
        v = v.strip()
        if not (1 <= len(v) <= 120):
            raise ValueError("friendly_name must be 1-120 characters")
        return v

    # Validate that rustdesk_id is 1-64 characters, strip whitespace
    @validator("rustdesk_id")
    def validate_rustdesk_id(cls, v):
        v = v.strip()
        if not (1 <= len(v) <= 64):
            raise ValueError("rustdesk_id must be 1-64 characters")
        return v

    # Validate that local_ip is valid IPv4 or IPv6 when provided
    @validator("local_ip")
    def validate_local_ip(cls, v):
        if v is not None:
            try:
                ipaddress.ip_address(v)
            except ValueError:
                raise ValueError("local_ip must be a valid IPv4 or IPv6 address")
        return v

    # Validate that tags are comma-separated, each ≤ 40 characters, strip and rejoin
    @validator("tags")
    def validate_tags(cls, v):
        if v is not None:
            tags = [tag.strip() for tag in v.split(",") if tag.strip()]
            if any(len(tag) > 40 for tag in tags):
                raise ValueError("Each tag must be 40 characters or less")
            return ",".join(tags)
        return v

    # Strip leading/trailing whitespace from all TEXT fields before persistence
    @validator("friendly_name", "rustdesk_id", "hostname", "local_ip", "operating_system", "username", "location", "notes", "tags", pre=True)
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class ComputerUpdate(BaseModel):
    friendly_name: Optional[str] = None
    rustdesk_id: Optional[str] = None
    hostname: Optional[str] = None
    local_ip: Optional[str] = None
    operating_system: Optional[str] = None
    username: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None

    # When a field is provided, validate it according to ComputerCreate rules
    @validator("friendly_name")
    def validate_friendly_name(cls, v):
        if v is not None:
            v = v.strip()
            if not (1 <= len(v) <= 120):
                raise ValueError("friendly_name must be 1-120 characters")
        return v

    @validator("rustdesk_id")
    def validate_rustdesk_id(cls, v):
        if v is not None:
            v = v.strip()
            if not (1 <= len(v) <= 64):
                raise ValueError("rustdesk_id must be 1-64 characters")
        return v

    @validator("local_ip")
    def validate_local_ip(cls, v):
        if v is not None:
            try:
                ipaddress.ip_address(v)
            except ValueError:
                raise ValueError("local_ip must be a valid IPv4 or IPv6 address")
        return v

    @validator("tags")
    def validate_tags(cls, v):
        if v is not None:
            tags = [tag.strip() for tag in v.split(",") if tag.strip()]
            if any(len(tag) > 40 for tag in tags):
                raise ValueError("Each tag must be 40 characters or less")
            return ",".join(tags)
        return v

    # Strip leading/trailing whitespace from all TEXT fields before persistence
    @validator("friendly_name", "rustdesk_id", "hostname", "local_ip", "operating_system", "username", "location", "notes", "tags", pre=True)
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class ComputerOut(BaseModel):
    id: int
    friendly_name: str
    rustdesk_id: str
    hostname: Optional[str] = None
    local_ip: Optional[str] = None
    operating_system: Optional[str] = None
    username: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

def casual_greeting(name: str) -> str:
    return f"Hi {name}, welcome to the phonebook app!"
