"""
Static checks on src/phonebook/static/app.js.

The JS can't be executed from pytest, so we assert on its source: it must define
``copyToClipboard`` (clipboard write + "Copied!" tooltip) and may omit
``confirmDelete`` since HTMX handles ``hx-confirm`` natively.
"""
from pathlib import Path

import pytest

APP_JS = Path(__file__).resolve().parents[1] / "src" / "phonebook" / "static" / "app.js"


@pytest.fixture
def source() -> str:
    return APP_JS.read_text(encoding="utf-8")


def test_defines_copy_to_clipboard(source):
    assert "function copyToClipboard(" in source


def test_calls_clipboard_write_text(source):
    assert "navigator.clipboard.writeText(" in source


def test_shows_copied_tooltip(source):
    assert "Copied!" in source


def test_confirm_delete_is_omitted(source):
    # HTMX hx-confirm replaces a custom confirmDelete handler.
    assert "function confirmDelete(" not in source


def test_no_module_syntax(source):
    # app.js is a classic script loaded with <script defer>; module syntax would break it
    import re

    assert not re.search(r"^\s*(import|export)\b", source, flags=re.M)


def test_copy_feedback_uses_styled_toast(source):
    assert "toast.className" in source
    assert "'toast toast-error'" in source


def test_base_template_loads_app_js():
    base = APP_JS.parents[1] / "templates" / "base.html"

    assert '<script src="/static/app.js" defer></script>' in base.read_text(encoding="utf-8")
