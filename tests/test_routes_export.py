"""Tests for the JSON/CSV export routes."""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from phonebook.crud import create_computer


def _sample(**overrides):
    data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "operating_system": "Windows 10",
        "username": "testuser",
        "location": "Office",
        "notes": "Test computer for export",
        "tags": "work, development",
    }
    data.update(overrides)
    return data


@pytest.mark.asyncio
async def test_export_json(client: AsyncClient, db_session: Session):
    create_computer(db_session, _sample())

    response = await client.get("/export/json")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()
    assert len(data) == 1
    assert data[0]["hostname"] == "test-host"
    assert data[0]["operating_system"] == "Windows 10"


@pytest.mark.asyncio
async def test_export_json_empty(client: AsyncClient, db_session: Session):
    response = await client.get("/export/json")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_export_csv(client: AsyncClient, db_session: Session):
    create_computer(db_session, _sample())

    response = await client.get("/export/csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "test-host" in response.text


@pytest.mark.asyncio
async def test_export_csv_has_header_when_empty(client: AsyncClient, db_session: Session):
    response = await client.get("/export/csv")
    assert response.status_code == 200
    # Header row is always present even with no records.
    assert "friendly_name" in response.text
    assert "rustdesk_id" in response.text
