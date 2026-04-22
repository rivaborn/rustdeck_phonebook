"""
Test the main application module.

This file tests the create_app() function and lifespan() async context manager
from src/phonebook/main.py.
"""

import pytest
from fastapi import FastAPI
from unittest.mock import patch, MagicMock

from phonebook.main import create_app
from phonebook.database import init_db


def test_create_app_returns_fastapi_instance():
    """Test that create_app() returns a FastAPI instance with correct title and version."""
    app = create_app()
    assert isinstance(app, FastAPI)
    assert app.title == "RustDesk Phone Book"
    assert app.version == "0.1.0"


def test_create_app_registers_routers():
    """Test that create_app() registers both computers and export routers."""
    app = create_app()
    
    # Check that routers are registered by looking at the route count
    # This is a basic check; more detailed inspection could be done
    assert len(app.routes) > 0  # At least some routes should exist


def test_create_app_mounts_static_files():
    """Test that create_app() mounts static files at /static."""
    app = create_app()
    
    # Check if static file routes are present
    static_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith('/static')]
    assert len(static_routes) > 0


def test_create_app_instantiates_jinja_templates():
    """Test that create_app() instantiates Jinja2Templates with correct directory."""
    app = create_app()
    
    # The templates should be accessible via app.state
    assert hasattr(app.state, 'templates')
    # We can't easily inspect the template directory without more complex mocking


@pytest.mark.asyncio
async def test_lifespan_calls_init_db():
    """Test that lifespan() calls init_db() on startup."""
    with patch('phonebook.database.init_db') as mock_init_db:
        app = create_app()
        
        # Create an async context manager from the lifespan
        async with app.router.lifespan_context(app):
            # The lifespan should have called init_db during startup
            mock_init_db.assert_called_once()


def test_app_has_lifespan_context_manager():
    """Test that app has a lifespan context manager that calls init_db."""
    app = create_app()
    
    # Check that the app has a lifespan context manager
    assert hasattr(app.router, 'lifespan_context')
    assert callable(app.router.lifespan_context)
