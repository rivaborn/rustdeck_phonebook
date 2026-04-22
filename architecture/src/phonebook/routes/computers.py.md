# src/phonebook/routes/computers.py

## Purpose
Handles HTTP routes for managing computer records including listing, viewing, creating, updating, and deleting computers with HTML responses and HTMX support.

## Responsibilities
- Define FastAPI routes for computer CRUD operations
- Render HTML templates for computer forms and details
- Handle database interactions through CRUD functions
- Support HTMX partial updates for dynamic UI
- Manage HTTP exceptions and validation errors

## Key Types
- ComputerCreate (Schema): Data validation for creating new computers
- ComputerUpdate (Schema): Data validation for updating existing computers
- Computer (Model): Database model representing computer records

## Key Functions
### list_computers
- Purpose: Returns list of all computers with optional HTMX support
- Calls: get_all_computers, templates.TemplateResponse

### new_computer_form
- Purpose: Displays form for creating new computer
- Calls: templates.TemplateResponse

### computer_detail
- Purpose: Shows detailed view of specific computer
- Calls: get_computer, templates.TemplateResponse

### create_computer_route
- Purpose: Creates new computer record with error handling
- Calls: create_computer, templates.TemplateResponse, RedirectResponse

### update_computer_route
- Purpose: Updates existing computer record with error handling
- Calls: update_computer, templates.TemplateResponse, RedirectResponse

### delete_computer_route
- Purpose: Deletes computer record with error handling
- Calls: delete_computer, templates.TemplateResponse, RedirectResponse

### search_computers_route
- Purpose: Searches computers by query string
- Calls: search_computers, templates.TemplateResponse

## Globals
- router (APIRouter): FastAPI router instance for computer endpoints
- templates (Jinja2Templates): Template engine for HTML rendering

## Dependencies
- fastapi, sqlalchemy, phonebook.database, phonebook.crud, phonebook.schemas, phonebook.models
- Jinja2 templates in
