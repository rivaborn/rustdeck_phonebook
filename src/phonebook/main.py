from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .database import init_db
from .routes import computers, export
from typing import AsyncGenerator
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for the FastAPI application."""
    # Call init_db() to initialize database.
    try:
        init_db()
    except Exception as e:
        logger.critical(f"Database init failed: {e}")
        raise
    
    # Yield control to app.
    yield
    
    # On app shutdown, no cleanup needed.
    # (Database connections are managed by SQLAlchemy's session lifecycle.)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    # Get settings using get_settings().
    settings = get_settings()
    
    # Create FastAPI app with title "RustDesk Phone Book", version "0.1.0", and debug flag from settings.
    app = FastAPI(
        title="RustDesk Phone Book",
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan
    )
    
    # Register routers from phonebook.routes.computers and phonebook.routes.export.
    app.include_router(computers.router)
    app.include_router(export.router)
    
    # Mount static files at "/static" pointing to "src/phonebook/static/".
    app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
    
    # Instantiate Jinja2Templates with directory "src/phonebook/templates/".
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
    
    # Return app.
    return app

# Create the global app instance
app = create_app()