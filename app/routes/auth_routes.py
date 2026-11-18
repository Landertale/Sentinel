"""
Thin authentication routes for Sentinel.
Handles user registration, login, session teardown, and session lifetime extension.
"""

import time
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
    jsonify
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration.
    Supports roles: analyst, admin, and employee.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "analyst").strip()

        if role not in ("analyst", "admin", "employee"):
            role = "analyst"

        auth_service = current_app.auth_service
        user = auth_service.register(username=username, password=password, role=role)

        if user:
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Username already exists. Please select another.", "danger")

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login.
    Authenticates with bcrypt-hashed credentials and initializes 10-minute session.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        auth_service = current_app.auth_service
        user = auth_service.login(username=username, password=password)

        if user:
            # Session setup with 10-minute activity tracking
            session.permanent = True
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            session["last_activity"] = time.time()
            flash(f"Welcome back, {user.username} ({user.role.title()})", "success")
            return redirect(url_for("incidents.list_incidents"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["GET"])
def logout():
    """
    Clear session and log out the user.
    """
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/extend-session", methods=["POST"])
def extend_session():
    """
    Extend active user session by resetting the 10-minute inactivity timer.
    Called asynchronously from the expiration popup modal.
    """
    if "user_id" in session:
        session["last_activity"] = time.time()
        session.modified = True
        return jsonify({
            "status": "success",
            "message": "Session successfully extended by 10 minutes."
        })
    return jsonify({"status": "error", "message": "No active session."}), 401
