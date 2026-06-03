import ipaddress
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


def _normalize_tags(value: Optional[str]) -> Optional[str]:
    """Split on commas, strip each tag, drop empties, enforce length, rejoin."""
    if value is None:
        return None
    tags = [tag.strip() for tag in value.split(",") if tag.strip()]
    if any(len(tag) > 40 for tag in tags):
        raise ValueError("Each tag must be 40 characters or less")
    if not tags:
        return None
    return ", ".join(tags)


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

    # Strip leading/trailing whitespace from all TEXT fields before validation.
    @field_validator(
        "friendly_name", "rustdesk_id", "hostname", "local_ip",
        "operating_system", "username", "location", "notes", "tags",
        mode="before",
    )
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("friendly_name")
    @classmethod
    def validate_friendly_name(cls, v):
        if not (1 <= len(v) <= 120):
            raise ValueError("friendly_name must be 1-120 characters")
        return v

    @field_validator("rustdesk_id")
    @classmethod
    def validate_rustdesk_id(cls, v):
        if not (1 <= len(v) <= 64):
            raise ValueError("rustdesk_id must be 1-64 characters")
        return v

    @field_validator("local_ip")
    @classmethod
    def validate_local_ip(cls, v):
        if v is not None:
            try:
                ipaddress.ip_address(v)
            except ValueError:
                raise ValueError("local_ip must be a valid IPv4 or IPv6 address")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        return _normalize_tags(v)


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

    @field_validator(
        "friendly_name", "rustdesk_id", "hostname", "local_ip",
        "operating_system", "username", "location", "notes", "tags",
        mode="before",
    )
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("friendly_name")
    @classmethod
    def validate_friendly_name(cls, v):
        if v is not None and not (1 <= len(v) <= 120):
            raise ValueError("friendly_name must be 1-120 characters")
        return v

    @field_validator("rustdesk_id")
    @classmethod
    def validate_rustdesk_id(cls, v):
        if v is not None and not (1 <= len(v) <= 64):
            raise ValueError("rustdesk_id must be 1-64 characters")
        return v

    @field_validator("local_ip")
    @classmethod
    def validate_local_ip(cls, v):
        if v is not None:
            try:
                ipaddress.ip_address(v)
            except ValueError:
                raise ValueError("local_ip must be a valid IPv4 or IPv6 address")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        return _normalize_tags(v)


class ComputerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
