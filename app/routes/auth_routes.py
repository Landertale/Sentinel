"""
Thin authentication routes for Sentinel.
Handles user registration, login, and session teardown.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration.
    Parses request -> delegates to AuthService -> redirects to login or renders view.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "analyst").strip()

        # NOTE (R19 Shortcut): Zero input validation on username and password format/length
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
    Parses request -> delegates to AuthService -> sets session attributes -> redirects.
    
    NOTE (R19 Shortcut): No rate limiting, no lockout, no CSRF token check,
    plain-text credentials matched.
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        auth_service = current_app.auth_service
        user = auth_service.login(username=username, password=password)

        if user:
            # Session setup
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
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
