"""
Route blueprint exports for Sentinel web layer.
"""

from app.routes.auth_routes import auth_bp
from app.routes.incident_routes import incident_bp
from app.routes.main_routes import main_bp

__all__ = ["auth_bp", "incident_bp", "main_bp"]
