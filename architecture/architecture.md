# Architecture Overview

## Repository Shape
- `src/` contains the main application code organized into packages
- `src/phonebook/` is the primary application package handling computer inventory management
- Configuration and database layers are separated into dedicated modules
- API routes and data models are organized under the phonebook package

## Major Subsystems

### Configuration Management
- Purpose: Handles application settings using Pydantic for validation and caching
- Key files: `src/phonebook/config.py`
- Dependencies: None

### Database Layer
- Purpose: Manages database connections, sessions, and ORM model definitions
- Key files: `src/phonebook/database.py`, `src/phonebook/models.py`
- Dependencies: Configuration management

### Data Access
- Purpose: Provides CRUD operations for computer entities with search capabilities
- Key files: `src/phonebook/crud.py`
- Dependencies: Database layer

### API Routes
- Purpose: Defines HTTP endpoints for computer management and data export
- Key files: `src/phonebook/routes/computers.py`, `src/phonebook/routes/export.py`
- Dependencies: Data access layer, configuration management

### Application Core
- Purpose: Sets up the FastAPI application with routing, database initialization, and static file serving
- Key files: `src/phonebook/main.py`
- Dependencies: All other subsystems

## Key Runtime Flows

### Initialization
- Application starts by loading cached configuration
- Database engine is created and sessions are configured
- SQLAlchemy models are initialized
- FastAPI application is configured with routes and static file serving

### Main Loop / Per-Frame
- HTTP server listens for incoming requests
- Route handlers process requests and interact with CRUD operations
- Database sessions are managed for each request
- Data is validated using Pydantic schemas before processing

### Shutdown
- Database sessions are properly closed
- Application gracefully terminates

## Notable Details
- Application uses Pydantic for configuration and data validation
- SQLAlchemy ORM handles database operations with timestamp tracking
- FastAPI framework provides RESTful API endpoints
- HTMX support enables dynamic UI updates
- Global settings instance provides cached configuration access
- Clear separation between data models, business logic, and API interfaces
