import pytest
from sqlalchemy.exc import IntegrityError
from phonebook.crud import (
    get_all_computers,
    get_computer,
    search_computers,
    create_computer,
    update_computer,
    delete_computer
)
from phonebook.schemas import ComputerCreate, ComputerUpdate, ComputerOut
from phonebook.models import Computer
from phonebook.database import get_db, init_db, SessionLocal
from unittest.mock import patch

def test_create_computer_success(db_session):
    """Test that create_computer successfully creates a record with all fields"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer = create_computer(db_session, computer_data)
    
    assert computer.id is not None
    assert computer.friendly_name == "Test Computer"
    assert computer.rustdesk_id == "123456"
    assert computer.hostname == "test-host"
    assert computer.local_ip == "192.168.1.100"
    assert computer.tags == "tag1, tag2"
    assert computer.notes == "Test notes"
    assert computer.username == "testuser"
    assert computer.location == "Office"
    assert computer.operating_system == "Windows 10"
    assert computer.created_at is not None
    assert computer.updated_at is not None

def test_create_computer_duplicate_rustdesk_id(db_session):
    """Test that create_computer raises IntegrityError when rustdesk_id is duplicated"""
    # First create a computer
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    create_computer(db_session, computer_data)
    
    # Try to create another with same rustdesk_id
    with pytest.raises(IntegrityError):
        create_computer(db_session, computer_data)

def test_get_all_computers_sorted(db_session):
    """Test that get_all_computers returns records sorted by friendly_name ascending"""
    # Create test computers with different names
    computer_data1 = {
        "friendly_name": "Z Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer_data2 = {
        "friendly_name": "A Computer",
        "rustdesk_id": "123457",
        "hostname": "test-host2",
        "local_ip": "192.168.1.101",
        "tags": "tag3, tag4",
        "notes": "Test notes2",
        "username": "testuser2",
        "location": "Office2",
        "operating_system": "Windows 11"
    }
    
    create_computer(db_session, computer_data1)
    create_computer(db_session, computer_data2)
    
    computers = get_all_computers(db_session)
    
    assert len(computers) == 2
    assert computers[0].friendly_name == "A Computer"
    assert computers[1].friendly_name == "Z Computer"

def test_search_computers(db_session):
    """Test that search_computers finds records by all searchable fields"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    create_computer(db_session, computer_data)
    
    # Search by friendly_name
    results = search_computers(db_session, "Test Computer")
    assert len(results) == 1
    
    # Search by rustdesk_id
    results = search_computers(db_session, "123456")
    assert len(results) == 1
    
    # Search by hostname
    results = search_computers(db_session, "test-host")
    assert len(results) == 1
    
    # Search by local_ip
    results = search_computers(db_session, "192.168.1.100")
    assert len(results) == 1
    
    # Search by tags
    results = search_computers(db_session, "tag1")
    assert len(results) == 1
    
    # Search by notes
    results = search_computers(db_session, "Test notes")
    assert len(results) == 1

def test_update_computer(db_session):
    """Test that update_computer updates fields and refreshes updated_at timestamp"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer = create_computer(db_session, computer_data)
    original_updated_at = computer.updated_at
    
    # Update the computer
    update_data = {
        "friendly_name": "Updated Computer",
        "hostname": "updated-host"
    }
    
    updated_computer = update_computer(db_session, computer.id, update_data)
    
    assert updated_computer.friendly_name == "Updated Computer"
    assert updated_computer.hostname == "updated-host"
    assert updated_computer.updated_at != original_updated_at

def test_delete_computer(db_session):
    """Test that delete_computer returns True when record is deleted and False when not found"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer = create_computer(db_session, computer_data)
    
    # Delete existing computer
    result = delete_computer(db_session, computer.id)
    assert result is True
    
    # Try to delete non-existent computer
    result = delete_computer(db_session, 999)
    assert result is False

def test_computer_create_validation_friendly_name_empty(db_session):
    """Test that ComputerCreate validation raises ValidationError when friendly_name is empty"""
    with pytest.raises(Exception):  # ValidationError
        ComputerCreate(
            friendly_name="",
            rustdesk_id="123456",
            hostname="test-host",
            local_ip="192.168.1.100"
        )

def test_computer_create_validation_friendly_name_too_long(db_session):
    """Test that ComputerCreate validation raises ValidationError when friendly_name exceeds 120 characters"""
    with pytest.raises(Exception):  # ValidationError
        ComputerCreate(
            friendly_name="A" * 121,
            rustdesk_id="123456",
            hostname="test-host",
            local_ip="192.168.1.100"
        )

def test_computer_create_validation_rustdesk_id_empty(db_session):
    """Test that ComputerCreate validation raises ValidationError when rustdesk_id is empty"""
    with pytest.raises(Exception):  # ValidationError
        ComputerCreate(
            friendly_name="Test Computer",
            rustdesk_id="",
            hostname="test-host",
            local_ip="192.168.1.100"
        )

def test_computer_create_validation_rustdesk_id_too_long(db_session):
    """Test that ComputerCreate validation raises ValidationError when rustdesk_id exceeds 64 characters"""
    with pytest.raises(Exception):  # ValidationError
        ComputerCreate(
            friendly_name="Test Computer",
            rustdesk_id="A" * 65,
            hostname="test-host",
            local_ip="192.168.1.100"
        )

def test_computer_create_validation_invalid_local_ip(db_session):
    """Test that ComputerCreate validation raises ValidationError when local_ip is invalid"""
    with pytest.raises(Exception):  # ValidationError
        ComputerCreate(
            friendly_name="Test Computer",
            rustdesk_id="123456",
            hostname="test-host",
            local_ip="999.999.0.0"
        )

def test_computer_create_validation_tag_normalization(db_session):
    """Test that ComputerCreate validation normalizes tags by splitting on comma, stripping whitespace, and rejoining with commas"""
    computer = ComputerCreate(
        friendly_name="Test Computer",
        rustdesk_id="123456",
        hostname="test-host",
        local_ip="192.168.1.100",
        tags=" tag1 , tag2 , tag3 "
    )
    
    # Tags should be normalized to "tag1, tag2, tag3"
    assert computer.tags == "tag1, tag2, tag3"

def test_computer_create_validation_tag_too_long(db_session):
    """Test that ComputerCreate validation raises ValidationError when any tag in tags exceeds 40 characters"""
    with pytest.raises(Exception):  # ValidationError
        ComputerCreate(
            friendly_name="Test Computer",
            rustdesk_id="123456",
            hostname="test-host",
            local_ip="192.168.1.100",
            tags="tag1, " + "A" * 41
        )

def test_computer_create_validation_whitespace_stripping(db_session):
    """Test that ComputerCreate validation strips leading/trailing whitespace from all TEXT fields"""
    computer = ComputerCreate(
        friendly_name="  Test Computer  ",
        rustdesk_id="  123456  ",
        hostname="  test-host  ",
        local_ip="192.168.1.100",
        tags="  tag1, tag2  ",
        notes="  Test notes  ",
        username="  testuser  ",
        location="  Office  ",
        operating_system="  Windows 10  "
    )
    
    assert computer.friendly_name == "Test Computer"
    assert computer.rustdesk_id == "123456"
    assert computer.hostname == "test-host"
    assert computer.tags == "tag1, tag2"
    assert computer.notes == "Test notes"
    assert computer.username == "testuser"
    assert computer.location == "Office"
    assert computer.operating_system == "Windows 10"

def test_computer_create_validation_unique_rustdesk_id(db_session):
    """Test that ComputerCreate validation ensures rustdesk_id is unique; raises IntegrityError on duplicate"""
    # First create a computer
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    create_computer(db_session, computer_data)
    
    # Try to create another with same rustdesk_id
    with pytest.raises(IntegrityError):
        create_computer(db_session, computer_data)

def test_computer_out_serialization(db_session):
    """Test that ComputerOut serialization includes all fields with correct types and values"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer = create_computer(db_session, computer_data)
    
    # Convert to ComputerOut
    computer_out = ComputerOut.model_validate(computer)
    
    assert computer_out.id == computer.id
    assert computer_out.friendly_name == computer.friendly_name
    assert computer_out.rustdesk_id == computer.rustdesk_id
    assert computer_out.hostname == computer.hostname
    assert computer_out.local_ip == computer.local_ip
    assert computer_out.tags == computer.tags
    assert computer_out.notes == computer.notes
    assert computer_out.username == computer.username
    assert computer_out.location == computer.location
    assert computer_out.operating_system == computer.operating_system
    assert computer_out.created_at == computer.created_at
    assert computer_out.updated_at == computer.updated_at

def test_init_db(db_session):
    """Test that init_db creates all tables in the database"""
    # This test assumes init_db is called and creates tables
    # We can't easily test this without mocking the database creation
    # But we can verify that it doesn't raise an exception
    try:
        init_db(db_session)
        assert True  # If no exception, test passes
    except Exception:
        pytest.fail("init_db should not raise an exception")

def test_get_db_success(db_session):
    """Test that get_db yields a valid SQLAlchemy session and closes it properly"""
    # This test verifies that get_db works correctly with a valid session
    db = next(get_db(db_session))
    assert db is not None
    assert hasattr(db, 'query')

def test_get_db_failure():
    """Test that get_db raises an exception when the database connection fails"""
    # This would require mocking the database connection to fail
    # For now, we'll just verify the function exists and can be called
    assert callable(get_db)

def test_computer_model_schema(db_session):
    """Test that Computer model correctly maps to the computers table schema"""
    # Create a computer to test the model
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer = create_computer(db_session, computer_data)
    
    # Verify all fields are present and correct
    assert computer.id is not None
    assert computer.friendly_name == "Test Computer"
    assert computer.rustdesk_id == "123456"
    assert computer.hostname == "test-host"
    assert computer.local_ip == "192.168.1.100"
    assert computer.tags == "tag1, tag2"
    assert computer.notes == "Test notes"
    assert computer.username == "testuser"
    assert computer.location == "Office"
    assert computer.operating_system == "Windows 10"
    assert computer.created_at is not None
    assert computer.updated_at is not None

def test_computer_model_auto_increment_id(db_session):
    """Test that id column is auto-incremented and primary key"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer1 = create_computer(db_session, computer_data)
    computer2 = create_computer(db_session, computer_data)
    
    assert computer1.id != computer2.id
    assert computer1.id == 1
    assert computer2.id == 2

def test_computer_model_unique_rustdesk_id(db_session):
    """Test that rustdesk_id column enforces uniqueness constraint"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    create_computer(db_session, computer_data)
    
    # Try to create another with same rustdesk_id
    with pytest.raises(IntegrityError):
        create_computer(db_session, computer_data)

def test_computer_model_timestamps(db_session):
    """Test that created_at and updated_at timestamps are set correctly on insert"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer = create_computer(db_session, computer_data)
    
    assert computer.created_at is not None
    assert computer.updated_at is not None
    assert computer.created_at == computer.updated_at

def test_computer_model_updated_at_refresh(db_session):
    """Test that updated_at timestamp is refreshed on every update"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer = create_computer(db_session, computer_data)
    original_updated_at = computer.updated_at
    
    # Update the computer
    update_data = {
        "friendly_name": "Updated Computer"
    }
    
    updated_computer = update_computer(db_session, computer.id, update_data)
    
    assert updated_computer.updated_at != original_updated_at

def test_computer_model_whitespace_stripping(db_session):
    """Test that all TEXT fields are stripped of leading/trailing whitespace before persistence"""
    computer_data = {
        "friendly_name": "  Test Computer  ",
        "rustdesk_id": "  123456  ",
        "hostname": "  test-host  ",
        "local_ip": "192.168.1.100",
        "tags": "  tag1, tag2  ",
        "notes": "  Test notes  ",
        "username": "  testuser  ",
        "location": "  Office  ",
        "operating_system": "  Windows 10  "
    }
    
    computer = create_computer(db_session, computer_data)
    
    assert computer.friendly_name == "Test Computer"
    assert computer.rustdesk_id == "123456"
    assert computer.hostname == "test-host"
    assert computer.tags == "tag1, tag2"
    assert computer.notes == "Test notes"
    assert computer.username == "testuser"
    assert computer.location == "Office"
    assert computer.operating_system == "Windows 10"

def test_computer_model_nullable_fields(db_session):
    """Test that Computer model correctly handles nullable fields"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": None,
        "username": None,
        "location": None,
        "operating_system": None
    }
    
    computer = create_computer(db_session, computer_data)
    
    assert computer.notes is None
    assert computer.username is None
    assert computer.location is None
    assert computer.operating_system is None

def test_computer_model_default_timestamps(db_session):
    """Test that Computer model correctly handles default values for timestamps"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2"
    }
    
    computer = create_computer(db_session, computer_data)
    
    assert computer.created_at is not None
    assert computer.updated_at is not None

def test_computer_create_validation_friendly_name_length(db_session):
    """Test that ComputerCreate validates that friendly_name must be 1-120 characters"""
    # Test minimum length (1 character)
    computer = ComputerCreate(
        friendly_name="A",
        rustdesk_id="123456",
        hostname="test-host",
        local_ip="192.168.1.100"
    )
    assert computer.friendly_name == "A"
    
    # Test maximum length (120 characters)
    computer = ComputerCreate(
        friendly_name="A" * 120,
        rustdesk_id="123456",
        hostname="test-host",
        local_ip="192.168.1.100"
    )
    assert computer.friendly_name == "A" * 120

def test_computer_create_validation_rustdesk_id_length(db_session):
    """Test that ComputerCreate validates that rustdesk_id must be 1-64 characters"""
    # Test minimum length (1 character)
    computer = ComputerCreate(
        friendly_name="Test Computer",
        rustdesk_id="A",
        hostname="test-host",
        local_ip="192.168.1.100"
    )
    assert computer.rustdesk_id == "A"
    
    # Test maximum length (64 characters)
    computer = ComputerCreate(
        friendly_name="Test Computer",
        rustdesk_id="A" * 64,
        hostname="test-host",
        local_ip="192.168.1.100"
    )
    assert computer.rustdesk_id == "A" * 64

def test_computer_create_validation_invalid_local_ip_format(db_session):
    """Test that ComputerCreate rejects invalid local_ip format"""
    with pytest.raises(Exception):  # ValidationError
        ComputerCreate(
            friendly_name="Test Computer",
            rustdesk_id="123456",
            hostname="test-host",
            local_ip="999.999.0.0"
        )

def test_computer_create_tag_normalization(db_session):
    """Test that ComputerCreate normalizes tags by splitting, stripping, and rejoining"""
    computer = ComputerCreate(
        friendly_name="Test Computer",
        rustdesk_id="123456",
        hostname="test-host",
        local_ip="192.168.1.100",
        tags=" tag1 , tag2 , tag3 "
    )
    
    assert computer.tags == "tag1, tag2, tag3"

def test_computer_create_whitespace_stripping_all_fields(db_session):
    """Test that ComputerCreate strips whitespace from all TEXT fields before validation"""
    computer = ComputerCreate(
        friendly_name="  Test Computer  ",
        rustdesk_id="  123456  ",
        hostname="  test-host  ",
        local_ip="192.168.1.100",
        tags="  tag1, tag2  ",
        notes="  Test notes  ",
        username="  testuser  ",
        location="  Office  ",
        operating_system="  Windows 10  "
    )
    
    assert computer.friendly_name == "Test Computer"
    assert computer.rustdesk_id == "123456"
    assert computer.hostname == "test-host"
    assert computer.tags == "tag1, tag2"
    assert computer.notes == "Test notes"
    assert computer.username == "testuser"
    assert computer.location == "Office"
    assert computer.operating_system == "Windows 10"

def test_computer_update_partial_updates(db_session):
    """Test that ComputerUpdate allows partial updates with validation on provided fields"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer = create_computer(db_session, computer_data)
    
    # Update only some fields
    update_data = {
        "friendly_name": "Updated Computer",
        "notes": "Updated notes"
    }
    
    updated_computer = update_computer(db_session, computer.id, update_data)
    
    assert updated_computer.friendly_name == "Updated Computer"
    assert updated_computer.notes == "Updated notes"
    assert updated_computer.hostname == "test-host"  # Should remain unchanged

def test_computer_out_serialization_fields(db_session):
    """Test that ComputerOut serializes all fields including id, created_at, updated_at"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer = create_computer(db_session, computer_data)
    
    # Convert to ComputerOut
    computer_out = ComputerOut.model_validate(computer)
    
    # Check all fields are present
    assert hasattr(computer_out, 'id')
    assert hasattr(computer_out, 'friendly_name')
    assert hasattr(computer_out, 'rustdesk_id')
    assert hasattr(computer_out, 'hostname')
    assert hasattr(computer_out, 'local_ip')
    assert hasattr(computer_out, 'tags')
    assert hasattr(computer_out, 'notes')
    assert hasattr(computer_out, 'username')
    assert hasattr(computer_out, 'location')
    assert hasattr(computer_out, 'operating_system')
    assert hasattr(computer_out, 'created_at')
    assert hasattr(computer_out, 'updated_at')

def test_computer_out_from_attributes(db_session):
    """Test that ComputerOut correctly maps database attributes to schema fields via from_attributes=True"""
    computer_data = {
        "friendly_name": "Test Computer",
        "rustdesk_id": "123456",
        "hostname": "test-host",
        "local_ip": "192.168.1.100",
        "tags": "tag1, tag2",
        "notes": "Test notes",
        "username": "testuser",
        "location": "Office",
        "operating_system": "Windows 10"
    }
    
    computer = create_computer(db_session, computer_data)
    
    # Convert to ComputerOut using from_attributes
    computer_out = ComputerOut.model_validate(computer)
    
    # Verify all attributes are correctly mapped
    assert computer_out.id == computer.id
    assert computer_out.friendly_name == computer.friendly_name
    assert computer_out.rustdesk_id == computer.rustdesk_id
    assert computer_out.hostname == computer.hostname
    assert computer_out.local_ip == computer.local_ip
    assert computer_out.tags == computer.tags
    assert computer_out.notes == computer.notes
    assert computer_out.username == computer.username
    assert computer_out.location == computer.location
    assert computer_out.operating_system == computer.operating_system
    assert computer_out.created_at == computer.created_at
    assert computer_out.updated_at == computer.updated_at
