import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from phonebook.crud import (
    create_computer,
    delete_computer,
    get_computer,
    search_computers,
    update_computer,
)
from phonebook.schemas import ComputerCreate

def test_search_computers_empty_query_raises_valueerror(db_session: Session):
    with pytest.raises(ValueError):
        search_computers(db_session, "")


def test_get_computer_missing_id_returns_none(db_session: Session):
    assert get_computer(db_session, 9999) is None


def test_update_computer_missing_id_returns_none(db_session: Session):
    fake_data = {"friendly_name": "Nonexistent"}
    assert update_computer(db_session, 9999, fake_data) is None


def test_delete_computer_missing_id_returns_false(db_session: Session):
    assert delete_computer(db_session, 9999) is False


def test_create_computer_invalid_ip_rejected_at_validation():
    # Validation happens at the route boundary via the schema; CRUD assumes
    # already-validated input (see AGENTS.md).
    with pytest.raises(ValidationError):
        ComputerCreate(friendly_name="Test", rustdesk_id="123", local_ip="invalid-IP")