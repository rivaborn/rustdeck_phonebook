"""
update_computer semantics: only fields the caller set are applied, an explicit
None clears an optional column, and the required columns are never cleared.
"""
from phonebook.crud import create_computer, update_computer
from phonebook.schemas import ComputerCreate, ComputerUpdate

FULL = {
    "friendly_name": "Office PC",
    "rustdesk_id": "123456789",
    "hostname": "office-pc",
    "local_ip": "10.0.0.12",
    "operating_system": "Windows 11",
    "username": "admin",
    "location": "Saginaw",
    "notes": "Front desk",
    "tags": "office,windows",
}


def test_unset_fields_are_kept(db_session):
    computer = create_computer(db_session, ComputerCreate(**FULL))

    updated = update_computer(db_session, computer.id, ComputerUpdate(location="Holy Cross"))

    assert updated.location == "Holy Cross"
    assert updated.username == "admin"
    assert updated.notes == "Front desk"


def test_explicit_none_clears_optional_field(db_session):
    computer = create_computer(db_session, ComputerCreate(**FULL))

    updated = update_computer(db_session, computer.id, ComputerUpdate(notes=None, username=None))

    assert updated.notes is None
    assert updated.username is None
    assert updated.hostname == "office-pc"


def test_required_fields_are_never_cleared(db_session):
    computer = create_computer(db_session, ComputerCreate(**FULL))

    updated = update_computer(
        db_session, computer.id, ComputerUpdate(friendly_name=None, rustdesk_id=None)
    )

    assert updated.friendly_name == "Office PC"
    assert updated.rustdesk_id == "123456789"


def test_plain_dict_updates_only_given_keys(db_session):
    computer = create_computer(db_session, ComputerCreate(**FULL))

    updated = update_computer(db_session, computer.id, {"location": None, "notes": "moved"})

    assert updated.location is None
    assert updated.notes == "moved"
    assert updated.username == "admin"
