"""
HTMX behaviour of the computer routes: form rendering and re-rendering with
per-field errors, HX-Refresh after saves, clearing fields on edit, search and
empty states, and the restyled page wiring.
"""
import re

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from phonebook.crud import create_computer, get_all_computers
from phonebook.schemas import ComputerCreate

HX = {"HX-Request": "true"}

FULL = {
    "friendly_name": "Office PC",
    "rustdesk_id": "123456789",
    "hostname": "office-pc",
    "local_ip": "10.0.0.12",
    "operating_system": "Windows 11",
    "username": "admin",
    "location": "Saginaw",
    "notes": "Front desk",
    "tags": "office, windows",
}


def seed(db_session, **overrides):
    return create_computer(db_session, ComputerCreate(**{**FULL, **overrides}))


def field_errors(html):
    return dict(re.findall(r'id="(\w+)-error">([^<]+)<', html))


def row_ids(html):
    return re.findall(r'<tr id="computer-(\d+)">', html)


# --- page -------------------------------------------------------------------

async def test_index_empty_state(client: AsyncClient, db_session: Session):
    response = await client.get("/")

    assert "No computers yet" in response.text
    assert "0 total" in response.text


async def test_index_lists_rows_with_actions(client: AsyncClient, db_session: Session):
    computer = seed(db_session)

    response = await client.get("/")

    assert row_ids(response.text) == [str(computer.id)]
    assert "1 total" in response.text
    assert "copyToClipboard('123456789')" in response.text
    assert f'hx-get="/computers/{computer.id}/edit"' in response.text
    assert f'hx-delete="/computers/{computer.id}"' in response.text


async def test_search_input_wiring(client: AsyncClient, db_session: Session):
    response = await client.get("/")

    search_input = re.search(r'<input[^>]*id="search-input"[^>]*>', response.text).group(0)
    assert 'hx-get="/computers/search"' in search_input
    assert 'name="q"' in search_input
    assert 'hx-target="#computer-table-body"' in search_input
    assert "search" in re.search(r'hx-trigger="([^"]*)"', search_input).group(1).split(", ")


# --- forms ------------------------------------------------------------------

async def test_new_form_posts_into_modal(client: AsyncClient, db_session: Session):
    response = await client.get("/computers/new", headers=HX)

    assert response.status_code == 200
    assert "Add computer" in response.text
    assert 'hx-post="/computers"' in response.text
    assert "hx-put" not in response.text
    assert 'hx-target="#modal"' in response.text


async def test_edit_form_prefilled_and_puts_into_modal(client: AsyncClient, db_session: Session):
    computer = seed(db_session)

    response = await client.get(f"/computers/{computer.id}/edit", headers=HX)

    assert "Edit computer" in response.text
    assert f'hx-put="/computers/{computer.id}"' in response.text
    assert "hx-post" not in response.text
    assert 'hx-target="#modal"' in response.text
    assert 'value="admin"' in response.text
    assert ">Front desk</textarea>" in response.text


# --- create -----------------------------------------------------------------

async def test_create_refreshes_page(client: AsyncClient, db_session: Session):
    response = await client.post("/computers", data=FULL, headers=HX)

    assert response.status_code == 200
    assert response.headers["HX-Refresh"] == "true"
    [computer] = get_all_computers(db_session)
    assert computer.operating_system == "Windows 11"
    assert computer.location == "Saginaw"


async def test_create_errors_shown_per_field(client: AsyncClient, db_session: Session):
    data = {**FULL, "friendly_name": "", "local_ip": "999.1.1.1"}

    response = await client.post("/computers", data=data, headers=HX)

    assert response.status_code == 200
    assert "HX-Refresh" not in response.headers
    errors = field_errors(response.text)
    assert errors["friendly_name"] == "This field is required"
    assert "valid IPv4 or IPv6" in errors["local_ip"]
    assert 'aria-invalid="true"' in response.text
    assert 'value="Windows 11"' in response.text
    assert get_all_computers(db_session) == []


async def test_create_errors_without_htmx_are_422(client: AsyncClient, db_session: Session):
    response = await client.post("/computers", data={"rustdesk_id": "1"})

    assert response.status_code == 422
    assert field_errors(response.text)["friendly_name"] == "This field is required"


async def test_create_duplicate_keeps_input(client: AsyncClient, db_session: Session):
    seed(db_session)

    response = await client.post("/computers", data={**FULL, "friendly_name": "Another"}, headers=HX)

    assert response.status_code == 200
    assert "already exists" in response.text
    assert 'value="Another"' in response.text
    assert len(get_all_computers(db_session)) == 1


# --- update -----------------------------------------------------------------

async def test_update_refreshes_page(client: AsyncClient, db_session: Session):
    computer = seed(db_session)

    response = await client.put(
        f"/computers/{computer.id}", data={**FULL, "location": "Holy Cross"}, headers=HX
    )

    assert response.headers["HX-Refresh"] == "true"
    db_session.refresh(computer)
    assert computer.location == "Holy Cross"


async def test_update_blank_input_clears_field(client: AsyncClient, db_session: Session):
    computer = seed(db_session)

    await client.put(
        f"/computers/{computer.id}", data={**FULL, "notes": "", "username": "  "}, headers=HX
    )

    db_session.refresh(computer)
    assert computer.notes is None
    assert computer.username is None
    assert computer.hostname == "office-pc"


async def test_update_requires_friendly_name(client: AsyncClient, db_session: Session):
    computer = seed(db_session)

    response = await client.put(
        f"/computers/{computer.id}", data={**FULL, "friendly_name": ""}, headers=HX
    )

    assert field_errors(response.text)["friendly_name"] == "This field is required"
    assert f'hx-put="/computers/{computer.id}"' in response.text
    db_session.refresh(computer)
    assert computer.friendly_name == "Office PC"


async def test_update_missing_computer_404(client: AsyncClient, db_session: Session):
    response = await client.put("/computers/999", data=FULL, headers=HX)

    assert response.status_code == 404


# --- search -----------------------------------------------------------------

@pytest.mark.parametrize("q", ["office", "OFFICE", "1234", "10.0.0", "windows"])
async def test_search_matches(client: AsyncClient, db_session: Session, q):
    match = seed(db_session)
    seed(db_session, friendly_name="Lab Mac", rustdesk_id="987", hostname="lab", local_ip=None,
         notes=None, tags="mac")

    response = await client.get("/computers/search", params={"q": q}, headers=HX)

    assert response.status_code == 200
    assert row_ids(response.text) == [str(match.id)]


async def test_search_no_match_empty_state(client: AsyncClient, db_session: Session):
    seed(db_session)

    response = await client.get("/computers/search", params={"q": "zzz"}, headers=HX)

    assert row_ids(response.text) == []
    assert "No computers match" in response.text


@pytest.mark.parametrize("params", [{"q": ""}, {"q": "   "}, {}])
async def test_blank_search_lists_everything(client: AsyncClient, db_session: Session, params):
    seed(db_session)
    seed(db_session, friendly_name="Lab Mac", rustdesk_id="987")

    response = await client.get("/computers/search", params=params, headers=HX)

    assert response.status_code == 200
    assert len(row_ids(response.text)) == 2
