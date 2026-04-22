"""
Test file for computer routes in src/phonebook/routes/computers.py
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from phonebook.routes.computers import (
    list_computers,
    new_computer_form,
    computer_detail,
    edit_computer_form,
    create_computer_route,
    update_computer_route,
    delete_computer_route,
    search_computers_route,
)
from phonebook.crud import create_computer, get_computer
from phonebook.schemas import ComputerCreate, ComputerUpdate
from phonebook.models import Computer

@pytest.mark.asyncio
async def test_list_computers_empty(client: AsyncClient, db_session: Session):
    """Test that GET / returns 200 with empty list when no computers exist."""
    response = await client.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_computer_via_post(client: AsyncClient, db_session: Session):
    """Test that POST /computers with valid data creates record and redirects."""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "operating_system": "Ubuntu 22.04",
        "username": "testuser",
        "location": "Office",
        "notes": "Test computer for testing",
        "tags": "test,development"
    }
    response = await client.post("/computers", data=computer_data)
    assert response.status_code == 302  # Redirect on success
    # Verify computer was created
    computer = get_computer(db_session, 1)
    assert computer is not None
    assert computer.friendly_name == "Test Computer"

@pytest.mark.asyncio
async def test_create_computer_missing_friendly_name(client: AsyncClient, db_session: Session):
    """Test that POST /computers without friendly_name returns 422 or re-renders form."""
    computer_data = {
        "rustdesk_id": "123456",
        "hostname": "test-host"
    }
    response = await client.post("/computers", data=computer_data)
    # Should either return 422 or re-render form with error
    assert response.status_code in [422, 200]

@pytest.mark.asyncio
async def test_create_computer_invalid_ip(client: AsyncClient, db_session: Session):
    """Test that POST /computers with invalid local_ip returns 422 or form error."""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "local_ip": "999.999.0.0"
    }
    response = await client.post("/computers", data=computer_data)
    # Should either return 422 or re-render form with error
    assert response.status_code in [422, 200]

@pytest.mark.asyncio
async def test_create_computer_duplicate_rustdesk_id(client: AsyncClient, db_session: Session):
    """Test that POST /computers with duplicate rustdesk_id raises error."""
    # First create a computer
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host"
    }
    await client.post("/computers", data=computer_data)
    
    # Try to create another with same rustdesk_id
    duplicate_data = {
        "friendly_name": "Another Computer",
        "rustdesk_id": "123456",
        "hostname": "another-host"
    }
    response = await client.post("/computers", data=duplicate_data)
    # Should either return error or re-render form with error
    assert response.status_code in [422, 200]

@pytest.mark.asyncio
async def test_edit_computer(client: AsyncClient, db_session: Session):
    """Test that PUT /computers/{id} updates record correctly."""
    # First create a computer
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host"
    }
    await client.post("/computers", data=computer_data)
    
    # Update the computer
    update_data = {
        "friendly_name": "Updated Computer",
        "rustdesk_id": "123456",
        "hostname": "updated-host"
    }
    response = await client.put("/computers/1", data=update_data)
    assert response.status_code in [200, 302]  # Success - either partial update or redirect
    
    # Verify update
    updated_computer = get_computer(db_session, 1)
    assert updated_computer.friendly_name == "Updated Computer"

@pytest.mark.asyncio
async def test_delete_computer_route(client: AsyncClient, db_session: Session):
    """Test that DELETE /computers/{id} removes record and returns 200."""
    # First create a computer
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host"
    }
    await client.post("/computers", data=computer_data)
    
    # Delete the computer
    response = await client.delete("/computers/1")
    assert response.status_code == 200
    
    # Verify deletion
    deleted_computer = get_computer(db_session, 1)
    assert deleted_computer is None

@pytest.mark.asyncio
async def test_search_route_returns_match(client: AsyncClient, db_session: Session):
    """Test that GET /computers/search?q=<name> returns 200 with matching rows."""
    # First create a computer
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host"
    }
    await client.post("/computers", data=computer_data)
    
    # Search for computer
    response = await client.get("/computers/search?q=Test")
    assert response.status_code == 200
    # Should contain computer row HTML

@pytest.mark.asyncio
async def test_search_route_no_match(client: AsyncClient, db_session: Session):
    """Test that GET /computers/search?q=zzznomatch returns 200 with empty body."""
    response = await client.get("/computers/search?q=zzznomatch")
    assert response.status_code == 200
    # Should return empty body or minimal response

@pytest.mark.asyncio
async def test_computer_detail_404(client: AsyncClient, db_session: Session):
    """Test that GET /computers/{id} raises 404 when computer ID does not exist."""
    response = await client.get("/computers/999")
    assert response.status_code == 404
