"""
Checks on src/phonebook/static/style.css (the real file, not a mock).

Encodes the design-system rules: tokens on :root, dark theme via both the
data-theme attribute and prefers-color-scheme, no hard-coded colors outside
the token blocks, reduced-motion support, and no external CSS framework.
"""
import re
from pathlib import Path

import pytest

CSS_PATH = Path(__file__).resolve().parents[1] / "src" / "phonebook" / "static" / "style.css"
COLOR_LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(")


@pytest.fixture(scope="module")
def css():
    return CSS_PATH.read_text(encoding="utf-8")


def _strip_comments(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def _token_blocks_removed(css):
    """Return the stylesheet with every block that defines tokens removed."""
    text = _strip_comments(css)
    text = re.sub(r":root\s*\{[^}]*\}", "", text)
    text = re.sub(r":root\[data-theme=\"dark\"\]\s*\{[^}]*\}", "", text)
    text = re.sub(r":root:not\(\[data-theme=\"light\"\]\)\s*\{[^}]*\}", "", text)
    return text


def _tokens(block):
    return set(re.findall(r"(--[\w-]+)\s*:", block))


def test_light_tokens_defined_on_root(css):
    root = re.search(r":root\s*\{([^}]*)\}", css).group(1)

    for token in ("--surface", "--shadow-light", "--shadow-dark", "--text", "--accent",
                  "--danger", "--font-size-body", "--space-4", "--radius-panel",
                  "--shadow-raised", "--shadow-inset", "--duration"):
        assert token in _tokens(root), token


def test_dark_theme_by_attribute_and_media_query(css):
    by_attr = re.search(r":root\[data-theme=\"dark\"\]\s*\{([^}]*)\}", css)
    by_media = re.search(
        r"@media \(prefers-color-scheme: dark\)\s*\{\s*:root:not\(\[data-theme=\"light\"\]\)\s*\{([^}]*)\}",
        css,
    )
    assert by_attr and by_media

    # Both dark blocks redefine the same tokens
    assert _tokens(by_attr.group(1)) == _tokens(by_media.group(1))
    assert {"--surface", "--shadow-light", "--shadow-dark", "--text"} <= _tokens(by_attr.group(1))


def test_components_use_no_color_literals(css):
    rest = _token_blocks_removed(css)

    assert COLOR_LITERAL.findall(rest) == []


def test_every_referenced_token_is_defined(css):
    defined = _tokens(_strip_comments(css))
    used = set(re.findall(r"var\((--[\w-]+)", css))

    assert used - defined == set()


def test_focus_ring_uses_accent(css):
    rule = re.search(r":focus-visible\s*\{([^}]*)\}", css).group(1)

    assert "var(--accent)" in rule
    assert "outline-offset" in rule


def test_respects_reduced_motion(css):
    assert "@media (prefers-reduced-motion: reduce)" in css


def test_table_stacks_into_cards_below_desktop(css):
    assert "@media (max-width: 1023px)" in css
    assert "content: attr(data-label)" in css


def test_htmx_swap_targets_styled(css):
    assert "#modal:not(:empty)" in css
    assert ".htmx-request" in css


def test_state_classes_present(css):
    for selector in (".tag", ".field-error", ".form-error", ".empty-state", ".toast",
                     ".btn:disabled", ".btn-primary", ".btn-danger"):
        assert selector in css, selector


def test_no_external_css_framework(css):
    assert "@import" not in css
    for framework in ("bootstrap", "tailwind", "bulma", "foundation"):
        assert framework not in css.lower(), framework
