"""
Incident management routes for Sentinel.
Handles incident listing, search, detail viewing, creation, commenting,
status updating, admin incident deletion, and IDOR protection.
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
    List security incidents with search, severity filter, and status filter.
    Employees can only view their own incidents (IDOR protection).
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    search_term = request.args.get("q", "").strip()
    
    # Check severity query param first; fall back to cookie preference
    severity = request.args.get("severity")
    saved_preference = request.cookies.get("sentinel_severity_pref", "ALL")

    if severity is None:
        severity = saved_preference if saved_preference != "ALL" else None

    # Status filter
    status = request.args.get("status")

    # Employee role restriction: employees can ONLY view their own reported incidents
    created_by_filter = None
    if session.get("role") == "employee":
        created_by_filter = session.get("username")

    incident_service = current_app.incident_service
    incidents = incident_service.list_incidents(
        search_term=search_term if search_term else None,
        severity_filter=severity if severity and severity != "ALL" else None,
        status_filter=status if status and status != "ALL" else None,
        created_by=created_by_filter
    )

    return render_template(
        "incidents/list.html",
        incidents=incidents,
        search_term=search_term,
        selected_severity=severity or "ALL",
        selected_status=status or "ALL",
        saved_preference=saved_preference
    )


@incident_bp.route("/incidents/new", methods=["GET", "POST"])
def create_incident():
    """
    Create a new incident.
    Accepts title, description, severity, status, assigned_to, source URL, and attachment.
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    auth_service = current_app.auth_service
    analysts = auth_service.get_analysts()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        severity = request.form.get("severity", "MEDIUM").strip()
        source_url = request.form.get("source_url", "").strip()
        attachment_file = request.files.get("attachment")

        # Status & assignment handling
        status = request.form.get("status", "New").strip()
        assigned_to = request.form.get("assigned_to", "").strip() or None

        # Employees cannot assign or set custom status
        if session.get("role") == "employee":
            status = "New"
            assigned_to = None
        elif status != "Assigned to":
            assigned_to = None

        if not title:
            flash("Incident title is required.", "danger")
            return render_template("incidents/create.html", analysts=analysts)

        incident_service = current_app.incident_service
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")

        incident = incident_service.create_incident(
            title=title,
            description=description,
            severity=severity,
            created_by=session.get("username", "Unknown"),
            source_url=source_url if source_url else None,
            attachment_file=attachment_file,
            upload_folder=upload_folder,
            status=status,
            assigned_to=assigned_to
        )

        flash(f"Incident #{incident.id} created successfully.", "success")
        return redirect(url_for("incidents.detail_incident", incident_id=incident.id))

    return render_template("incidents/create.html", analysts=analysts)


@incident_bp.route("/incidents/<int:incident_id>", methods=["GET"])
def detail_incident(incident_id: int):
    """
    Detailed incident view displaying full incident reports, source preview, and comments.
    Enforces IDOR protection: employee role can only view their own incident.
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    incident_service = current_app.incident_service
    incident, comments = incident_service.get_incident_details(incident_id)

    if not incident:
        flash(f"Incident #{incident_id} not found.", "warning")
        return redirect(url_for("incidents.list_incidents"))

    # IDOR Protection: Employee cannot view incidents created by other users
    if session.get("role") == "employee" and incident.created_by != session.get("username"):
        flash("Access Denied (IDOR Protected): You do not have permission to view incidents created by other users.", "danger")
        return redirect(url_for("incidents.list_incidents"))

    auth_service = current_app.auth_service
    analysts = auth_service.get_analysts()

    return render_template(
        "incidents/detail.html",
        incident=incident,
        comments=comments,
        analysts=analysts
    )


@incident_bp.route("/incidents/<int:incident_id>/status", methods=["POST"])
def update_status(incident_id: int):
    """
    Update incident status ('New', 'Assigned to', 'Resolved') and assigned analyst.
    Employees are restricted from updating incident status.
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    incident_service = current_app.incident_service
    incident = incident_service.get_incident_by_id(incident_id)

    if not incident:
        flash(f"Incident #{incident_id} not found.", "warning")
        return redirect(url_for("incidents.list_incidents"))

    # IDOR & Role Protection: Employees cannot alter status
    if session.get("role") == "employee":
        flash("Access Denied: Employees cannot modify incident status or assignments.", "danger")
        return redirect(url_for("incidents.detail_incident", incident_id=incident_id))

    new_status = request.form.get("status", "New").strip()
    assigned_to = request.form.get("assigned_to", "").strip() or None

    if new_status not in ("New", "Assigned to", "Resolved"):
        new_status = "New"

    if new_status != "Assigned to":
        assigned_to = None

    incident_service.update_incident_status_and_assignee(incident_id, new_status, assigned_to)
    flash(f"Incident #{incident_id} updated to status '{new_status}'.", "success")
    return redirect(url_for("incidents.detail_incident", incident_id=incident_id))


@incident_bp.route("/incidents/<int:incident_id>/delete", methods=["POST"])
def delete_incident(incident_id: int):
    """
    Delete an incident.
    Only system administrators can delete incidents.
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    # Admin verification
    if session.get("role") != "admin":
        flash("Access Denied: Only administrators have permission to delete incidents.", "danger")
        return redirect(url_for("incidents.detail_incident", incident_id=incident_id))

    incident_service = current_app.incident_service
    incident = incident_service.get_incident_by_id(incident_id)

    if not incident:
        flash(f"Incident #{incident_id} not found.", "warning")
        return redirect(url_for("incidents.list_incidents"))

    incident_service.delete_incident(incident_id)
    flash(f"Incident #{incident_id} has been deleted successfully.", "success")
    return redirect(url_for("incidents.list_incidents"))


@incident_bp.route("/incidents/<int:incident_id>/comments", methods=["POST"])
def add_comment(incident_id: int):
    """
    Add a comment to an incident investigation.
    IDOR Protection: Employees can only comment on their own incidents.
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    incident_service = current_app.incident_service
    incident = incident_service.get_incident_by_id(incident_id)

    if not incident:
        flash(f"Incident #{incident_id} not found.", "warning")
        return redirect(url_for("incidents.list_incidents"))

    # IDOR Protection
    if session.get("role") == "employee" and incident.created_by != session.get("username"):
        flash("Access Denied (IDOR Protected): You cannot comment on incidents reported by other users.", "danger")
        return redirect(url_for("incidents.list_incidents"))

    content = request.form.get("content", "").strip()
    if content:
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
    response.set_cookie("sentinel_severity_pref", pref_severity, max_age=60*60*24*30)
    flash(f"Default severity filter preference updated to '{pref_severity}'.", "info")
    return response


@incident_bp.route("/uploads/<path:filename>", methods=["GET"])
def download_attachment(filename: str):
    """
    Serve uploaded incident attachment files.
    Enforces authorization check for employees (IDOR protection).
    """
    if not is_authenticated():
        return redirect(url_for("auth.login"))

    # IDOR Protection: If employee, verify the file belongs to an incident they created
    if session.get("role") == "employee":
        user_incidents = current_app.incident_service.list_incidents(created_by=session.get("username"))
        allowed_files = [i.attachment_filename for i in user_incidents if i.attachment_filename]
        if filename not in allowed_files:
            flash("Access Denied (IDOR Protected): You cannot download attachments from other users' incidents.", "danger")
            return redirect(url_for("incidents.list_incidents"))

    upload_folder = os.path.abspath(current_app.config.get("UPLOAD_FOLDER", "app/static/uploads"))
    return send_from_directory(upload_folder, filename, as_attachment=True)
