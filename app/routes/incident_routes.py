"""
Thin incident management routes for Sentinel.
Handles incident listing, search, detail viewing, creation, commenting, and cookie preferences.
"""

import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
    make_response,
    send_from_directory,
    abort
)

incident_bp = Blueprint("incidents", __name__)


def is_authenticated() -> bool:
    """Helper to check if active session contains authenticated user."""
    return "user_id" in session


@incident_bp.route("/incidents", methods=["GET"])
def list_incidents():
    """
    List security incidents with search and severity filter.
    Applies cookie-based filter preference if no query parameter is provided.
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    search_term = request.args.get("q", "").strip()
    
    # Check query param first; fall back to cookie preference
    severity = request.args.get("severity")
    saved_preference = request.cookies.get("sentinel_severity_pref", "ALL")

    if severity is None:
        severity = saved_preference if saved_preference != "ALL" else None

    incident_service = current_app.incident_service
    incidents = incident_service.list_incidents(
        search_term=search_term if search_term else None,
        severity_filter=severity if severity and severity != "ALL" else None
    )

    return render_template(
        "incidents/list.html",
        incidents=incidents,
        search_term=search_term,
        selected_severity=severity or "ALL",
        saved_preference=saved_preference
    )


@incident_bp.route("/incidents/new", methods=["GET", "POST"])
def create_incident():
    """
    Create a new incident.
    Accepts title, description, severity, source intelligence URL, and optional attachment.
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        severity = request.form.get("severity", "MEDIUM").strip()
        source_url = request.form.get("source_url", "").strip()
        attachment_file = request.files.get("attachment")

        if not title:
            flash("Incident title is required.", "danger")
            return render_template("incidents/create.html")

        incident_service = current_app.incident_service
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")

        incident = incident_service.create_incident(
            title=title,
            description=description,
            severity=severity,
            created_by=session.get("username", "Unknown"),
            source_url=source_url if source_url else None,
            attachment_file=attachment_file,
            upload_folder=upload_folder
        )

        flash(f"Incident #{incident.id} created successfully.", "success")
        return redirect(url_for("incidents.detail_incident", incident_id=incident.id))

    return render_template("incidents/create.html")


@incident_bp.route("/incidents/<int:incident_id>", methods=["GET"])
def detail_incident(incident_id: int):
    """
    Detailed incident view displaying full incident reports, source preview, and comments.
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    incident_service = current_app.incident_service
    incident, comments = incident_service.get_incident_details(incident_id)

    if not incident:
        flash(f"Incident #{incident_id} not found.", "warning")
        return redirect(url_for("incidents.list_incidents"))

    return render_template(
        "incidents/detail.html",
        incident=incident,
        comments=comments
    )


@incident_bp.route("/incidents/<int:incident_id>/comments", methods=["POST"])
def add_comment(incident_id: int):
    """
    Add a comment to an incident investigation.
    
    NOTE (R19 Shortcut): Content is received and stored without XSS sanitization.
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    content = request.form.get("content", "").strip()
    if content:
        incident_service = current_app.incident_service
        incident_service.add_comment(
            incident_id=incident_id,
            user_id=session["user_id"],
            username=session["username"],
            content=content
        )
        flash("Comment added to incident log.", "success")
    else:
        flash("Comment content cannot be empty.", "warning")

    return redirect(url_for("incidents.detail_incident", incident_id=incident_id))


@incident_bp.route("/preferences", methods=["POST"])
def set_preferences():
    """
    Store user preference for default list severity filter in an HTTP cookie.
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    pref_severity = request.form.get("default_severity", "ALL").strip()
    
    response = make_response(redirect(url_for("incidents.list_incidents")))
    # NOTE (R19 Shortcut): Cookie set without HttpOnly or Secure flags for simple prototype access
    response.set_cookie("sentinel_severity_pref", pref_severity, max_age=60*60*24*30)
    flash(f"Default severity filter preference updated to '{pref_severity}'.", "info")
    return response


@incident_bp.route("/uploads/<path:filename>", methods=["GET"])
def download_attachment(filename: str):
    """
    Serve uploaded incident attachment files directly.
    
    NOTE (R19 Shortcut): Direct file serving without authorization or mime-type validation.
    """
    upload_folder = os.path.abspath(current_app.config.get("UPLOAD_FOLDER", "app/static/uploads"))
    return send_from_directory(upload_folder, filename, as_attachment=True)
