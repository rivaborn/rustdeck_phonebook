# RustDesk Phone Book

A lightweight internal web application for managing RustDesk-managed computers/endpoints. This companion tool maintains a phone book of devices that can be accessed through a browser on a local network.

## What the app does

The RustDesk Phone Book application provides a web interface to:
- Add, edit, and delete computer records
- Search and view details of devices
- Export computer records in JSON and CSV formats
- Manage endpoints that are managed by RustDesk
- Serve as a standalone companion tool without modifying RustDesk source code

## Prerequisites

- Ubuntu 22.04 or higher
- Python 3.11 or higher
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rustdesk-phonebook
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Running in development

Start the application with auto-reload enabled:
