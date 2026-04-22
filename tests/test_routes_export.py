import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.phonebook.main import app
from src.phonebook.models import Computer
from src.phonebook.database import get_db

client = TestClient(app)

# Mock database dependency
def mock_get_db():
    db = MagicMock()
    yield db

# Test export_json function
def test_export_json():
    with patch('src.phonebook.database.get_db', side_effect=mock_get_db):
        # Mock computer data
        mock_computers = [
            Computer(
                id=1,
                hostname="test-host",
                friendly_name="Test Computer",
                local_ip="192.168.1.100",
                operating_system="Windows 10",
                username="testuser",
                location="Office",
                tags="work,development",
                notes="Test computer for export",
                rustdesk_id="123456"
            )
        ]
        
        # Mock the database query
        with patch('src.phonebook.crud.get_all_computers', return_value=mock_computers):
            response = client.get("/export/json")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"
            data = response.json()
            assert len(data) == 1
            assert data[0]["hostname"] == "test-host"

# Test export_csv function
def test_export_csv():
    with patch('src.phonebook.database.get_db', side_effect=mock_get_db):
        # Mock computer data
        mock_computers = [
            Computer(
                id=1,
                hostname="test-host",
                friendly_name="Test Computer",
                local_ip="192.168.1.100",
                operating_system="Windows 10",
                username="testuser",
                location="Office",
                tags="work,development",
                notes="Test computer for export",
                rustdesk_id="123456"
            )
        ]
        
        # Mock the database query
        with patch('src.phonebook.crud.get_all_computers', return_value=mock_computers):
            response = client.get("/export/csv")
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv"
            assert "test-host" in response.text
