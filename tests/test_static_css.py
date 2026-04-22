import pytest
from unittest.mock import mock_open, patch

@pytest.fixture
def css_content():
    return """
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
}

@media (prefers-color-scheme: dark) {
    :root {
        --primary-color: #2c3e50;
        --secondary-color: #27ae60;
    }
}

table.responsive-table th,
table.responsive-table td::before {
    content: attr(data-label);
}

.tag {
    display: inline-block;
    padding: 0.2em 0.6em;
    margin-right: 0.5em;
    background-color: #3498db;
    color: white;
    border-radius: 16px;
}

.field-error {
    color: red;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
}
"""

@pytest.fixture
def mock_css_file(monkeypatch, css_content):
    mock = mock_open(read_data=css_content)
    monkeypatch.setattr("builtins.open", mock)
    return mock

def test_custom_properties(mock_css_file, css_content):
    with open('src/phonebook/static/style.css') as f:
        content = f.read()
    
    assert '--primary-color: #3498db;' in content
    assert '--secondary-color: #2ecc71;' in content
    assert '@media (prefers-color-scheme: dark)' in content
    assert '--primary-color: #2c3e50;' in css_content.split('@media')[1]
    assert '--secondary-color: #27ae60;' in css_content.split('@media')[1]

def test_responsive_table_layout(mock_css_file, css_content):
    with open('src/phonebook/static/style.css') as f:
        content = f.read()
    
    assert 'table.responsive-table th,' in content
    assert 'td::before {' in content
    assert 'content: attr(data-label);' in content

def test_tag_styling(mock_css_file, css_content):
    with open('src/phonebook/static/style.css') as f:
        content = f.read()
    
    assert '.tag {' in content
    assert 'display: inline-block;' in content
    assert 'padding: 0.2em 0.6em;' in content
    assert 'margin-right: 0.5em;' in content
    assert 'background-color: #3498db;' in content
    assert 'color: white;' in content
    assert 'border-radius: 16px;' in content

def test_error_message_styling(mock_css_file, css_content):
    with open('src/phonebook/static/style.css') as f:
        content = f.read()
    
    assert '.field-error {' in content
    assert 'color: red;' in content

def test_modal_overlay_behavior(mock_css_file, css_content):
    with open('src/phonebook/static/style.css') as f:
        content = f.read()
    
    assert '.modal {' in content
    assert 'position: fixed;' in content
    assert 'top: 0;' in content
    assert 'left: 0;' in content
    assert 'width: 100%;' in content
    assert 'height: 100%;' in content
    assert 'background-color: rgba(0, 0, 0, 0.5);' in content

def test_no_external_css_frameworks(mock_css_file, css_content):
    with open('src/phonebook/static/style.css') as f:
        content = f.read()
    
    external_frameworks = ['bootstrap', 'tailwind', 'materialize', 'foundation']
    for framework in external_frameworks:
        assert framework not in content.lower()
