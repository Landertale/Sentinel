# Sentinel — Security Incident Management Platform

Internal web application prototype built for **Nexus Digital Solutions (NDS)** under the direction of CEO Miren Arriaga.

Sentinel provides security analysts with an incident tracking dashboard, threat intelligence link previewing, forensic log attachments, investigation timelines, and user preference cookies.

> ⚠️ **IMPORTANT NOTICE (R19):**  
> This initial base prototype intentionally omits security controls (plain-text passwords, string-interpolated raw SQL, raw HTML rendering in comments, unvalidated file uploads, and unvalidated URL fetching). Defensive engineering and hardening will be introduced in subsequent iterations. See [`VULNERABILITIES_AND_SHORTCUTS.md`](file:///home/zibr/Documentos/GitHub/Sentinel/VULNERABILITIES_AND_SHORTCUTS.md) for full documentation.

---

## 🏛️ Layered Architecture (3-Tier)

Sentinel strictly adheres to a modular 3-tier object-oriented architecture:

```text
Sentinel/
├── run.py                          # Application entry point
├── VULNERABILITIES_AND_SHORTCUTS.md # Dedicated register of all intentional shortcuts (R19)
├── app/
│   ├── __init__.py                 # Application factory (bootstrap & dependency injection)
│   ├── models/                     # Domain Entities (OOP encapsulation & inheritance)
│   │   ├── user.py                 # User (Base), Analyst, Admin hierarchy
│   │   ├── incident.py             # Incident domain entity
│   │   ├── comment.py              # Investigation comment entity
│   │   └── attachment.py           # Artifact attachment entity
│   ├── repositories/               # Data Access Layer (Abstract Base Classes & SQLite)
│   │   ├── base.py                 # Abstract Base Classes (Repository Pattern)
│   │   ├── database.py             # SQLite connection manager & schema initializer
│   │   ├── user_repository.py      # SQLite implementation of IUserRepository
│   │   ├── incident_repository.py  # SQLite implementation of IIncidentRepository
│   │   └── comment_repository.py   # SQLite implementation of ICommentRepository
│   ├── services/                   # Business Logic Layer
│   │   ├── auth_service.py         # Authentication logic (registration, credential check)
│   │   ├── incident_service.py     # Incident lifecycle, comments, searches, uploads
│   │   └── preview_service.py      # Threat intel URL <title> extraction
│   ├── routes/                     # Presentation / Web Layer (Thin Blueprints)
│   │   ├── auth_routes.py          # /login, /register, /logout
│   │   ├── incident_routes.py      # /incidents, /incidents/new, /incidents/<id>, /preferences
│   │   └── main_routes.py          # / redirector
│   ├── templates/                  # Jinja2 HTML templates (SOC Dark Theme)
│   │   ├── base.html
│   │   ├── auth/                   # login.html, register.html
│   │   └── incidents/              # list.html, create.html, detail.html
│   └── static/
│       ├── css/style.css           # Modern SOC cyber dark theme stylesheet
│       └── uploads/                # Local attachment storage
└── tests/                          # Automated test suite
    ├── test_auth.py                # Tests for R1 (Auth, User hierarchy)
    └── test_incidents.py           # Tests for R2 - R8 (Incidents, search, comments, preview, cookies)
```

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- Flask 3.x
- Requests

### 2. Run the Application
From the repository root:
```bash
python3 run.py
```
Open your browser at `http://127.0.0.1:5000`.

### 3. Run the Test Suite
```bash
python3 -m unittest discover tests
```

---

## 📋 Features Implemented

1. **Auth System (R1):** Full registration, login, session creation, and logout.
2. **Incident Management (R2, R3):** Incident creation form (title, description, severity), list view (most recent first), and incident detail view backed by persistent SQLite storage.
3. **Investigation Comments (R4 / Feature 1):** Incident timeline notes with raw HTML support.
4. **Substring Search (R5 / Feature 2):** Fast substring search across incident titles and descriptions.
5. **Artifact Attachments (R6 / Feature 3):** File uploads stored on the local filesystem with download links.
6. **Threat Intelligence Link Preview (R7 / Feature 4):** URL previewing with automatic `<title>` tag extraction.
7. **Filter Preferences (R8 / Feature 5):** Client cookie storage for default severity filters.
