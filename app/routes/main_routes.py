"""
Main entry routes for Sentinel.
"""

from flask import Blueprint, redirect, url_for, session

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    """
    Root route handler: redirects authenticated users to incident list,
    or redirects unauthenticated visitors to login page.
    """
    if "user_id" in session:
        return redirect(url_for("incidents.list_incidents"))
    return redirect(url_for("auth.login"))
