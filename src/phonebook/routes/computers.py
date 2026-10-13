import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from ..crud import (
    create_computer,
    delete_computer,
    get_all_computers,
    get_computer,
    search_computers,
    update_computer,
)
from ..database import get_db
from ..schemas import ComputerCreate, ComputerUpdate

router = APIRouter()
# Explicit directory path avoids template-cache resolution issues.
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir)


_FORM_FIELDS = (
    "friendly_name", "rustdesk_id", "hostname", "local_ip", "operating_system",
    "username", "location", "notes", "tags",
)


def _is_hx(request: Request) -> bool:
    return request.headers.get("HX-Request") is not None


async def _form_dict(request: Request) -> dict:
    """Read a urlencoded form body into a dict, mapping blank strings to None."""
    form = await request.form()
    data: dict = {}
    for key, value in form.items():
        if isinstance(value, str):
            value = value.strip()
            data[key] = value if value != "" else None
        else:
            data[key] = value
    return data


def _field_errors(exc: ValidationError) -> dict:
    """Map each invalid field to a human-readable message."""
    errors: dict = {}
    for err in exc.errors():
        field = str(err["loc"][0]) if err.get("loc") else "form"
        if err.get("type") == "missing" or err.get("input") is None:
            message = "This field is required"
        else:
            message = err.get("msg", "Invalid value").removeprefix("Value error, ")
        errors.setdefault(field, message)
    return errors


def _render_form(request: Request, computer, computer_id=None, errors=None, error=None):
    # HTMX only swaps 2xx responses, so a re-rendered form is 200 for HTMX and
    # 422 for a plain form post.
    return templates.TemplateResponse(
        request,
        "partials/computer_form.html",
        {
            "computer": computer,
            "computer_id": computer_id,
            "errors": errors or {},
            "error": error,
            "is_hx_request": _is_hx(request),
        },
        status_code=200 if (_is_hx(request) or not (errors or error)) else 422,
    )


def _saved(request: Request) -> Response:
    # Reload so the table, its count and the empty state all reflect the change
    # and the modal closes.
    if _is_hx(request):
        return Response(status_code=200, headers={"HX-Refresh": "true"})
    return RedirectResponse(url="/", status_code=302)


@router.get("/", response_class=HTMLResponse)
async def list_computers(request: Request, db=Depends(get_db)) -> Response:
    computers = get_all_computers(db)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"computers": computers, "is_hx_request": _is_hx(request)},
    )


@router.get("/computers/new", response_class=HTMLResponse)
async def new_computer_form(request: Request) -> Response:
    return _render_form(request, None)


# Must be declared before "/computers/{computer_id}" so "search" is not parsed as an id.
@router.get("/computers/search", response_class=HTMLResponse)
async def search_computers_route(request: Request, q: str = "", db=Depends(get_db)) -> Response:
    # A cleared search box shows every computer again (a 4xx would leave the
    # filtered rows on screen, since HTMX does not swap error responses).
    q = q.strip()
    computers = search_computers(db, q) if q else get_all_computers(db)
    return templates.TemplateResponse(
        request,
        "partials/computer_rows.html",
        {"computers": computers, "query": q, "is_hx_request": _is_hx(request)},
    )


@router.get("/computers/{computer_id}", response_class=HTMLResponse)
async def computer_detail(request: Request, computer_id: int, db=Depends(get_db)) -> Response:
    computer = get_computer(db, computer_id)
    if not computer:
        raise HTTPException(status_code=404, detail="Computer not found")
    return templates.TemplateResponse(
        request,
        "partials/computer_detail.html",
        {"computer": computer, "is_hx_request": _is_hx(request)},
    )


@router.get("/computers/{computer_id}/edit", response_class=HTMLResponse)
async def edit_computer_form(request: Request, computer_id: int, db=Depends(get_db)) -> Response:
    computer = get_computer(db, computer_id)
    if not computer:
        raise HTTPException(status_code=404, detail="Computer not found")
    return _render_form(request, computer, computer_id=computer_id)


@router.post("/computers", response_class=HTMLResponse)
async def create_computer_route(request: Request, db=Depends(get_db)) -> Response:
    raw = await _form_dict(request)
    try:
        form = ComputerCreate(**raw)
    except ValidationError as exc:
        return _render_form(request, raw, errors=_field_errors(exc))

    try:
        create_computer(db, form)
    except IntegrityError:
        db.rollback()
        return _render_form(request, raw, error="A computer with this RustDesk ID already exists")

    return _saved(request)


@router.put("/computers/{computer_id}", response_class=HTMLResponse)
async def update_computer_route(request: Request, computer_id: int, db=Depends(get_db)) -> Response:
    if not get_computer(db, computer_id):
        raise HTTPException(status_code=404, detail="Computer not found")

    raw = await _form_dict(request)
    try:
        # The edit form submits every field, so validate it like a create
        # (friendly_name and rustdesk_id required); blank optional fields clear.
        ComputerCreate(**raw)
        form = ComputerUpdate(**{field: raw.get(field) for field in _FORM_FIELDS})
    except ValidationError as exc:
        return _render_form(request, raw, computer_id=computer_id, errors=_field_errors(exc))

    try:
        update_computer(db, computer_id, form)
    except IntegrityError:
        db.rollback()
        return _render_form(
            request, raw, computer_id=computer_id,
            error="A computer with this RustDesk ID already exists",
        )

    return _saved(request)


@router.delete("/computers/{computer_id}")
async def delete_computer_route(request: Request, computer_id: int, db=Depends(get_db)) -> Response:
    # Delete is only ever invoked via HTMX (hx-delete); an empty 200 lets the
    # client swap the row out.
    delete_computer(db, computer_id)
    return Response(status_code=200)

