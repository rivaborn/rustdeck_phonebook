import os
from types import SimpleNamespace

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
    return templates.TemplateResponse(
        request,
        "partials/computer_form.html",
        {"computer": None, "is_hx_request": _is_hx(request)},
    )


# Must be declared before "/computers/{computer_id}" so "search" is not parsed as an id.
@router.get("/computers/search", response_class=HTMLResponse)
async def search_computers_route(request: Request, q: str, db=Depends(get_db)) -> Response:
    if not q or len(q.strip()) < 1:
        raise HTTPException(status_code=400, detail="Search query must be at least 1 character")
    computers = search_computers(db, q)
    return templates.TemplateResponse(
        request,
        "partials/computer_rows.html",
        {"computers": computers, "is_hx_request": _is_hx(request)},
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
    return templates.TemplateResponse(
        request,
        "partials/computer_form.html",
        {"computer": computer, "is_hx_request": _is_hx(request)},
    )


@router.post("/computers", response_class=HTMLResponse)
async def create_computer_route(request: Request, db=Depends(get_db)) -> Response:
    raw = await _form_dict(request)
    try:
        form = ComputerCreate(**raw)
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "partials/computer_form.html",
            {"computer": SimpleNamespace(**raw), "error": _first_error(exc), "is_hx_request": _is_hx(request)},
        )

    try:
        new_computer = create_computer(db, form)
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse(
            request,
            "partials/computer_form.html",
            {
                "computer": SimpleNamespace(**raw),
                "error": "A computer with this RustDesk ID already exists",
                "is_hx_request": _is_hx(request),
            },
        )

    if _is_hx(request):
        return templates.TemplateResponse(
            request,
            "partials/computer_row.html",
            {"computer": new_computer, "is_hx_request": True},
        )
    return RedirectResponse(url="/", status_code=302)


@router.put("/computers/{computer_id}", response_class=HTMLResponse)
async def update_computer_route(request: Request, computer_id: int, db=Depends(get_db)) -> Response:
    raw = await _form_dict(request)
    try:
        form = ComputerUpdate(**raw)
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "partials/computer_form.html",
            {
                "computer": SimpleNamespace(id=computer_id, **raw),
                "error": _first_error(exc),
                "is_hx_request": _is_hx(request),
            },
        )

    try:
        updated_computer = update_computer(db, computer_id, form)
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse(
            request,
            "partials/computer_form.html",
            {
                "computer": SimpleNamespace(id=computer_id, **raw),
                "error": "A computer with this RustDesk ID already exists",
                "is_hx_request": _is_hx(request),
            },
        )

    if not updated_computer:
        raise HTTPException(status_code=404, detail="Computer not found")

    if _is_hx(request):
        return templates.TemplateResponse(
            request,
            "partials/computer_row.html",
            {"computer": updated_computer, "is_hx_request": True},
        )
    return RedirectResponse(url="/", status_code=302)


@router.delete("/computers/{computer_id}")
async def delete_computer_route(request: Request, computer_id: int, db=Depends(get_db)) -> Response:
    # Delete is only ever invoked via HTMX (hx-delete); an empty 200 lets the
    # client swap the row out.
    delete_computer(db, computer_id)
    return Response(status_code=200)


def _first_error(exc: ValidationError) -> str:
    """Human-readable message from the first validation error."""
    errors = exc.errors()
    if not errors:
        return "Invalid input"
    err = errors[0]
    field = err.get("loc", ["field"])[0]
    return f"{field}: {err.get('msg', 'invalid value')}"
