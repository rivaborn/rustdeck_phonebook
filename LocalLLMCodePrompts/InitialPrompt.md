You are an expert full-stack software engineer. Build a small internal “Phone Book” web app for RustDesk.

Goal:
Create a lightweight web application that runs on my Ubuntu server and is reachable on my local network through a browser. The purpose of the app is to maintain a list of computers/endpoints that I use with RustDesk. The app should let me add a computer, edit a computer, and remove a computer.

Important context:
- This is for my local network / homelab use.
- The app should be simple, reliable, and easy to self-host.
- The UI should be clean and practical, not flashy.
- The finished result should be runnable on Ubuntu.
- RustDesk itself is an open-source remote desktop application and its repo is here for context: https://github.com/rustdesk/rustdesk
- The phone book app does NOT need to modify RustDesk source code.
- Prefer building this as a standalone companion web app that stores and manages RustDesk-related computer records.
- The app should be optimized for LAN use, not public internet scale.

What the app should do:
1. Show a list/table of saved computers.
2. Allow adding a new computer.
3. Allow editing an existing computer.
4. Allow deleting/removing a computer.
5. Allow searching/filtering the list.
6. Allow clicking a record to view its details.
7. Store the data persistently so entries survive reboot/restart.

Each computer record should support these fields:
- Friendly name
- RustDesk ID
- Hostname
- Local IP address
- Operating system
- Username / owner
- Physical location
- Notes
- Tags
- Date created
- Date updated

Functional expectations:
- Validate required fields when adding/editing.
- Prevent obviously invalid IP address formats.
- Confirm before deletion.
- Show success/error messages for actions.
- Sort records by friendly name by default.
- Search should match at least friendly name, RustDesk ID, hostname, IP, tags, and notes.

Technical preferences:
- Choose a stack that is easy to maintain on Ubuntu.
- Prioritize simplicity over overengineering.
- Good options would be:
  - Python + FastAPI + Jinja2 + SQLite + HTMX / minimal JS
  - or Node.js + Express + SQLite + server-rendered templates
- Pick the option you believe is best for fast implementation, clarity, and maintainability.
- Use SQLite for storage unless there is a compelling reason not to.
- Make the UI responsive enough to work on desktop and tablet browsers.
- Keep dependencies minimal.
- Organize the code clearly.

Security and deployment expectations:
- This is for local network use, but still avoid careless design.
- Sanitize inputs.
- Use parameterized DB queries / ORM protections.
- Do not expose secrets in code.
- Make host/port configurable with environment variables.
- Default bind should allow LAN access, for example 0.0.0.0 on a configurable port.
- Include instructions for running behind a reverse proxy, but do not require one.
- Include a systemd service example.
- Include a .env.example if environment variables are used.

Deliverables:
1. A complete runnable codebase.
2. A README with:
   - what the app does
   - prerequisites
   - how to install dependencies
   - how to run it in development
   - how to run it in production on Ubuntu
   - how to access it from another machine on the LAN
   - how to configure the port / host
   - how to back up the SQLite database
3. Database schema / migrations or startup initialization logic.
4. A sample seed dataset with a few example computers.
5. A systemd service file example.
6. Basic tests for the core CRUD behavior if practical.

Implementation guidance:
- First decide on the stack and briefly justify it.
- Then create the project structure.
- Then implement:
  - database model/schema
  - CRUD routes/handlers
  - templates/pages
  - validation
  - search/filtering
  - seed data
  - README
- Keep the UI server-rendered unless a tiny amount of JS is clearly helpful.
- Avoid unnecessary SPA complexity.
- Avoid Docker unless it meaningfully simplifies the result; if you include Docker, it should be optional.
- Make the code understandable for a solo self-hosting user.

Nice-to-have features if easy:
- Copy-to-clipboard button for RustDesk ID or IP
- Tag badges
- Simple import/export to JSON or CSV
- “Last seen edited” timestamp formatting
- Dark mode via basic CSS variables

What I want from you while coding:
- Make reasonable choices without asking too many questions.
- If you must choose between elegance and simplicity, choose simplicity.
- Output the full project files with their paths and contents.
- Ensure the result is internally consistent and runnable.
- Include any commands I need to create a virtual environment, install packages, initialize the database, and start the app on Ubuntu.
- At the end, provide a short “Quick Start” section for deployment on my Ubuntu server.

Please build this as if you are handing it to a technically comfortable homelab user who wants something dependable and easy to modify later.