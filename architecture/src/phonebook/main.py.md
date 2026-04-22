# src/phonebook/main.py

## Purpose
Configures and creates a FastAPI application for the RustDesk Phone Book backend, including routing, database initialization, and static file serving.

## Responsibilities
- Initialize and configure FastAPI application instance
- Register API routers for computers and export endpoints
- Set up static file serving and template directory
- Manage application lifespan with database initialization
- Create global application instance

## Key Types
- create_app (Function): Creates and configures FastAPI application
- lifespan (AsyncGenerator): Manages application lifecycle with database setup

## Key Functions
### create_app
- Purpose: Creates and configures the FastAPI application with settings, routers, and static files
- Calls: get_settings, init_db

### lifespan
- Purpose: Manages application startup and shutdown with database initialization
- Calls: init_db

## Globals
- app (FastAPI): Global application instance created by create_app function

## Dependencies
- fastapi.FastAPI: Main application class
- fastapi.templating.Jinja2Templates: Template rendering support
- src.phonebook.config.get_settings: Configuration loading
- src.phonebook.database.init_db: Database initialization
- src.phonebook.routes.computers.router: Computers API routes
- src.phonebook.routes.export.router: Export API routes
- typing.AsyncGenerator: Type hint for lifespan generator
