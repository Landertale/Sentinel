# Sentinel — Security Incident Management Platform (Prototype)
## Architectural Shortcuts & Intentional Vulnerability Register (R19)

**Author:** Nexus Digital Solutions (NDS) Engineering Team  
**Stakeholder:** CEO Miren Arriaga  
**Project Milestone:** Sprint 1 / Rapid Base Prototype (3-Week Target)  
**Status:** WORKING BASE PROTOTYPE — DEFENSIVE CONTROLS DEFERRED TO ITERATION 2

---

### 1. Executive Context & Scope

To meet CEO Miren Arriaga's accelerated 3-week internal launch timeline, the **Sentinel** Security Incident Management Platform was constructed using a clean 3-tier, object-oriented architecture prioritizing modularity, code readability, and core business workflows over immediate security hardening.

Per project constraints, **no defensive or defensive-in-depth code was introduced**. All security hardening, cryptographic controls, strict input validation, and sanitization routines have been deliberately postponed to subsequent engineering sprints.

This document serves as the formal register cataloging every deliberate shortcut, the affected system layer, the associated security risk (mapped to OWASP Top 10:2021), and the concrete remediation plan required before production release.

---

### 2. Comprehensive Shortcut & Vulnerability Matrix

| ID | Category | Component / File | Vulnerability / Shortcut Description | OWASP Top 10 Mapping | Remediation in Iteration 2 |
|---|---|---|---|---|---|
| **SC-01** | Authentication | `app/services/auth_service.py`, `app/models/user.py`, `app/repositories/user_repository.py` | **Plain-Text Passwords:** Passwords are received, persisted in SQLite, and verified in plain text without cryptographic hashing or salt (no bcrypt / argon2). | **A07:2021 – Identification & Authentication Failures** | Implement `werkzeug.security.generate_password_hash` and `check_password_hash` or Argon2id. |
| **SC-02** | Input Validation & Querying | `app/repositories/incident_repository.py`, `app/repositories/user_repository.py` | **Raw SQL Query Formatting (SQL Injection):** SQL queries are constructed using Python f-strings and string interpolation (e.g. search substring filtering, username lookups) rather than parameterized queries (`?`). | **A03:2021 – Injection** | Refactor all database interactions to parameterized statements: `cursor.execute("SELECT ... WHERE title LIKE ?", ('%' + term + '%',))`. |
| **SC-03** | Presentation & Rendering | `app/templates/incidents/detail.html`, `app/services/incident_service.py` | **Unescaped HTML Comments (Stored XSS):** Incident investigation comments are rendered using Jinja2's `| safe` filter without sanitization or HTML tag stripping, enabling arbitrary JavaScript execution. | **A03:2021 – Injection (Cross-Site Scripting)** | Remove `| safe` filter to enable automatic Jinja2 escaping; employ DOMPurify / Bleach if rich text formatting is required. |
| **SC-04** | Session & Request Integrity | `app/routes/auth_routes.py`, `app/routes/incident_routes.py`, All Templates | **Missing CSRF Protection:** Forms do not issue or validate anti-CSRF tokens. Requests can be forged by third-party origins when a user has an active session. | **A01:2021 – Broken Access Control** | Integrate Flask-WTF with CSRFProtect to validate tokens on all state-changing POST requests. |
| **SC-05** | File Handling | `app/services/incident_service.py`, `app/routes/incident_routes.py` | **Unvalidated File Uploads & Path Traversal Risk:** Incident attachment files are saved directly to `app/static/uploads` using the raw uploaded filename without checking extensions (allowing `.php`, `.py`, `.html`, `.exe`) or sanitizing paths. | **A04:2021 – Insecure Design** | Enforce allowed extension whitelist (e.g., `.pcap`, `.log`, `.txt`), generate random UUID file storage keys, and use `secure_filename`. |
| **SC-06** | Threat Intel Preview | `app/services/preview_service.py` | **Server-Side Request Forgery (SSRF):** The URL preview generator fetches user-supplied URLs via `urllib.request.urlopen` with zero validation. Attackers can probe internal loopback services (`127.0.0.1`, `localhost`) or cloud metadata endpoints (`169.254.169.254`). | **A10:2021 – Server-Side Request Forgery (SSRF)** | Restrict URL schemes to HTTP/HTTPS, resolve DNS before connection, and strictly block loopback, RFC 1918 private subnets, and link-local ranges. |
| **SC-07** | Session Management & Cookies | `app/__init__.py`, `app/routes/incident_routes.py` | **Insecure Session & Preference Cookies:** Cookies (including severity preferences) are stored without `HttpOnly`, `SameSite=Lax/Strict`, or `Secure` flags. Session cookies use default client-side signing. | **A05:2021 – Security Misconfiguration** | Set `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_SAMESITE='Lax'`, and configure server-side session caching (e.g. Redis). |
| **SC-08** | Cryptographic Secrets | `app/__init__.py` | **Hardcoded Weak Secret Key:** The Flask `SECRET_KEY` is hardcoded to a static string in `app/__init__.py`. | **A02:2021 – Cryptographic Failures** | Load `SECRET_KEY` strictly from environment variables or secure secret stores (e.g. HashiCorp Vault, AWS Secrets Manager). |
| **SC-09** | Application Server Configuration | `run.py` | **Debug Mode Enabled on Host 0.0.0.0:** The entry point binds to all network interfaces (`0.0.0.0`) with `debug=True`, exposing the interactive Werkzeug traceback debugger. | **A05:2021 – Security Misconfiguration** | Disable debug mode outside local development, bind to specific localhost addresses, and deploy behind a production WSGI server (Gunicorn/uWSGI). |

---

### 3. Detailed Technical Analysis of Shortcuts

#### 3.1 Plain-Text Passwords (SC-01)
- **Files:** `app/models/user.py`, `app/services/auth_service.py`, `app/repositories/user_repository.py`
- **Current Behavior:** The `users` database table stores raw user passwords. Authentication simply checks `user.password == password`.
- **Impact:** Any unauthorized access to `sentinel.db` or database extraction yields immediate compromise of all analyst credentials.

#### 3.2 Raw SQL Queries with String Interpolation (SC-02)
- **Files:** `app/repositories/incident_repository.py`, `app/repositories/user_repository.py`
- **Current Behavior:** The search and filter queries directly concatenate terms:
  ```python
  conditions.append(f"(title LIKE '%{search_term}%' OR description LIKE '%{search_term}%')")
  ```
- **Impact:** Attackers can inject SQL operators (e.g., `' OR '1'='1' --`) to bypass filters, extract data, or modify database state.

#### 3.3 Raw HTML Rendering in Comments (SC-03)
- **Files:** `app/templates/incidents/detail.html`
- **Current Behavior:** Comments are rendered using:
  ```jinja2
  <div class="comment-body">{{ comment.content | safe }}</div>
  ```
- **Impact:** Analysts posting `<script>` or event handlers (`<img src=x onerror=...>`) will have their scripts executed in the browser of any analyst or administrator viewing the incident.

#### 3.4 Unchecked External URL Fetching / SSRF (SC-04)
- **Files:** `app/services/preview_service.py`
- **Current Behavior:** `PreviewService.fetch_source_title(url)` issues a GET request to any string provided in the `source_url` field.
- **Impact:** Sentinel can be leveraged as an internal proxy to scan internal ports, access local administrative consoles, or query cloud instance metadata.

#### 3.5 Unrestricted File Uploads (SC-05)
- **Files:** `app/services/incident_service.py`, `app/routes/incident_routes.py`
- **Current Behavior:** Files are stored under `app/static/uploads/` using their original filename without extension restriction.
- **Impact:** Upload of executable files or HTML scripts could lead to stored XSS or remote execution depending on the server hosting configuration.

---

### 4. Roadmap for Iteration 2 (Hardening Sprint)

Upon sign-off from CEO Miren Arriaga and stakeholder review of the prototype, the following hardening steps will be implemented:

1. **Sprint 2A (Credentials & Sessions):**
   - Install `argon2-cffi` / `bcrypt`.
   - Implement database migration to hash existing passwords.
   - Configure secure session cookie flags (`HttpOnly`, `Secure`, `SameSite`).
   - Introduce Flask-WTF CSRF protection.

2. **Sprint 2B (Data Access Layer Parameterization):**
   - Rewrite all repository methods to use SQLite parameterized placeholders (`?`).
   - Remove all direct f-string SQL query assemblies.

3. **Sprint 2C (Content Sanitization & Safe Uploads):**
   - Remove `| safe` filter from Jinja2 templates.
   - Whitelist file extensions (`.txt`, `.log`, `.pcap`, `.json`, `.csv`).
   - Hash attachment filenames on disk and store metadata separately.
   - Validate external URLs against private IP subnets and loopback addresses.
