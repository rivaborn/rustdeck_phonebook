"""
Package initializer for the routes package.

This file makes the containing directory importable as a package
and may optionally re-export selected symbols from sibling modules.
"""

# Re-export symbols from sibling modules to make them easily accessible
# when importing from this package
from .computers import router, templates
