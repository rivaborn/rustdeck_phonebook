from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from phonebook.database import get_db
from phonebook.crud import (
    get_all_computers,
    get_computer,
    search_computers,
    create_computer,
    update_computer,
    delete_computer
)
from phonebook.schemas import ComputerCreate, ComputerUpdate
from phonebook.models import Computer

router = APIRouter()
templates = Jinja2Templates(directory="src/phonebook/templates")

@router.get("/", response_class=HTMLResponse)
async def list_computers(request: Request) -> Response:
    db = next(get_db())
    computers = get_all_computers(db)
    is_hx_request = request.headers.get("HX-Request") is not None
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "computers": computers, "is_hx_request": is_hx_request}
    )

@router.get("/computers/new", response_class=HTMLResponse)
async def new_computer_form(request: Request) -> Response:
    is_hx_request = request.headers.get("HX-Request") is not None
    return templates.TemplateResponse(
        "partials/computer_form.html",
        {"request": request, "computer": ComputerCreate(), "is_hx_request": is_hx_request}
    )

@router.get("/computers/{computer_id}", response_class=HTMLResponse)
async def computer_detail(request: Request, computer_id: int) -> Response:
    db = next(get_db())
    computer = get_computer(db, computer_id)
    if not computer:
        raise HTTPException(status_code=404, detail="Computer not found")
    is_hx_request = request.headers.get("HX-Request") is not None
    return templates.TemplateResponse(
        "partials/computer_detail.html",
        {"request": request, "computer": computer, "is_hx_request": is_hx_request}
    )

@router.get("/computers/{computer_id}/edit", response_class=HTMLResponse)
async def edit_computer_form(request: Request, computer_id: int) -> Response:
    db = next(get_db())
    computer = get_computer(db, computer_id)
    if not computer:
        raise HTTPException(status_code=404, detail="Computer not found")
    is_hx_request = request.headers.get("HX-Request") is not None
    return templates.TemplateResponse(
        "partials/computer_form.html",
        {"request": request, "computer": ComputerUpdate(**computer.__dict__), "is_hx_request": is_hx_request}
    )

@router.post("/computers", response_class=HTMLResponse)
async def create_computer_route(request: Request, form: ComputerCreate) -> Response:
    db = next(get_db())
    try:
        new_computer = create_computer(db, form)
        is_hx_request = request.headers.get("HX-Request") is not None
        if is_hx_request:
            return templates.TemplateResponse(
                "partials/computer_row.html",
                {"request": request, "computer": new_computer, "is_hx_request": is_hx_request}
            )
        else:
            return RedirectResponse(url="/", status_code=303)
    except IntegrityError:
        db.rollback()
        is_hx_request = request.headers.get("HX-Request") is not None
        return templates.TemplateResponse(
            "partials/computer_form.html",
            {"request": request, "computer": form, "error": "A computer with this RustDesk ID already exists", "is_hx_request": is_hx_request}
        )

@router.put("/computers/{computer_id}", response_class=HTMLResponse)
async def update_computer_route(request: Request, computer_id: int, form: ComputerUpdate) -> Response:
    db = next(get_db())
    try:
        updated_computer = update_computer(db, computer_id, form)
        if not updated_computer:
            raise HTTPException(status_code=404, detail="Computer not found")
        is_hx_request = request.headers.get("HX-Request") is not None
        if is_hx_request:
            return templates.TemplateResponse(
                "partials/computer_row.html",
                {"request": request, "computer": updated_computer, "is_hx_request": is_hx_request}
            )
        else:
            return RedirectResponse(url="/", status_code=303)
    except IntegrityError:
        db.rollback()
        is_hx_request = request.headers.get("HX-Request") is not None
        return templates.TemplateResponse(
            "partials/computer_form.html",
            {"request": request, "computer": form, "error": "A computer with this RustDesk ID already exists", "is_hx_request": is_hx_request}
        )

@router.delete("/computers/{computer_id}", response_class=HTMLResponse)
async def delete_computer_route(request: Request, computer_id: int) -> Response:
    db = next(get_db())
    try:
        delete_computer(db, computer_id)
        is_hx_request = request.headers.get("HX-Request") is not None
        if is_hx_request:
            return Response(status_code=200)
        else:
            return RedirectResponse(url="/", status_code=303)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=404, detail="Computer not found")

@router.get("/search", response_class=HTMLResponse)
async def search_computers_route(request: Request, q: str) -> Response:
    db = next(get_db())
    if not q or len(q.strip()) < 1:
        raise HTTPException(status_code=400, detail="Search query must be at least 1 character")
    computers = search_computers(db, q)
    is_hx_request = request.headers.get("HX-Request") is not None
    return templates.TemplateResponse(
        "partials/computer_row.html",
        {"request": request, "computers": computers, "is_hx_request": is_hx_request}
    )
