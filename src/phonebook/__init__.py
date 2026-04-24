"""
Standard Python package-marker file for the phonebook package.

This file makes the containing directory importable as a package and
(optionally) re-exports selected symbols from sibling modules to shorten
import paths.

Imports: no intra-project imports beyond any re-exports. If re-exports
are kept, their canonical source is the sibling module section that
owns each symbol (see other `## Module: src/...` sections).

Re-exports: optional, determined at implementation time. May be empty.
"""

from .config import Settings, get_settings
from .database import get_db, init_db
from .models import Base, Computer
from .crud import (
    create_computer,
    delete_computer,
    get_all_computers,
    get_computer,
    search_computers,
    update_computer
)
from .schemas import ComputerCreate, ComputerOut, ComputerUpdate
from .main import app, create_app, lifespan
