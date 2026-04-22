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

from .src.phonebook.config import Settings, get_settings
from .src.phonebook.database import get_db, init_db
from .src.phonebook.models import Base, Computer
from .src.phonebook.crud import (
    create_computer,
    delete_computer,
    get_all_computers,
    get_computer,
    search_computers,
    update_computer
)
from .src.phonebook.schemas import ComputerCreate, ComputerOut, ComputerUpdate
from .src.phonebook.main import app, create_app, lifespan
