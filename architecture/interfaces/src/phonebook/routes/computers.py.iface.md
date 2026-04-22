# Module: src/phonebook/routes/computers.py

## Role
FastAPI router implementing CRUD operations for computer resources with HTMX support.

## Contract: Module-level functions

### `list_computers(request) -> Response`
- **Requires:** `request` must be a valid FastAPI Request object with valid headers; database connection must be available via `get_db()` generator
- **Guarantees:** Returns HTMLResponse with rendered index.html template containing list of all computers
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `new_computer_form(request) -> Response`
- **Requires:** `request` must be a valid FastAPI Request object with valid headers
- **Guarantees:** Returns HTMLResponse with rendered computer_form.html template for new computer creation
- **Raises:** None
- **Silent failure:** None
- **Thread safety:** Unsafe

### `computer_detail(request, computer_id) -> Response`
- **Requires:** `request` must be a valid FastAPI Request object with valid headers; `computer_id` must be a positive integer; database connection must be available
- **Guarantees:** Returns HTMLResponse with rendered computer_detail.html template for specified computer
- **Raises:** `HTTPException` with status_code=404 if computer not found
- **Silent failure:** None
- **Thread safety:** Unsafe

### `edit_computer_form(request, computer_id) -> Response`
- **Requires:** `request` must be a valid FastAPI Request object with valid headers; `computer_id` must be a positive integer; database connection must be available
- **Guarantees:** Returns HTMLResponse with rendered computer_form.html template for editing specified computer
- **Raises:** `HTTPException` with status_code=404 if computer not found
- **Silent failure:** None
- **Thread safety:** Unsafe

### `create_computer_route(request, form) -> Response`
- **Requires:** `request` must be a valid FastAPI Request object with valid headers; `form` must be a valid ComputerCreate schema instance
- **Guarantees:** Returns HTMLResponse with rendered computer_row.html partial or redirects to root on success
- **Raises:** `HTTPException` with status_code=400 if IntegrityError occurs during creation (duplicate RustDesk ID)
- **Silent failure:** None
- **Thread safety:** Unsafe

### `update_computer_route(request, computer_id, form) -> Response`
- **Requires:** `request` must be a valid FastAPI Request object with valid headers; `computer_id` must be a positive integer; `form` must be a valid ComputerUpdate schema instance
- **Guarantees:** Returns HTMLResponse with rendered computer_row.html partial or redirects to root on success
- **Raises:** `HTTPException` with status_code=404 if computer not found or IntegrityError occurs (duplicate RustDesk ID)
- **Silent failure:** None
- **Thread safety:** Unsafe

### `delete_computer_route(request, computer_id) -> Response`
- **Requires:** `request` must be a valid FastAPI Request object with valid headers; `computer_id` must be a positive integer; database connection must be available
- **Guarantees:** Returns HTMLResponse with success status or redirects to root on
