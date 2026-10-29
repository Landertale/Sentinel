"""
Application factory for Sentinel Security Incident Management Platform.
Assembles the layered architecture: Database -> Repositories -> Services -> Blueprints.
"""

import os
from flask import Flask
from app.repositories import (
    DatabaseConnection,
    SQLiteUserRepository,
    SQLiteIncidentRepository,
    SQLiteCommentRepository
)
from app.services import (
    AuthService,
    IncidentService,
    PreviewService
)
from app.routes import auth_bp, incident_bp, main_bp


def create_app(test_config: dict = None) -> Flask:
    """
    Application factory pattern to configure and bootstrap the Flask application.
    
    :param test_config: Optional dictionary with configuration overrides (useful for testing)
    :return: Configured Flask application instance
    """
    app = Flask(__name__, instance_relative_config=True)

    # Base workspace directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_upload_dir = os.path.join(base_dir, "app", "static", "uploads")
    default_db_path = os.path.join(base_dir, "sentinel.db")

    # Default application configuration
    # NOTE (R19 Shortcut): Hardcoded weak SECRET_KEY, no secure session cookie flags
    app.config.from_mapping(
        SECRET_KEY="sentinel-insecure-prototype-secret-key",
        DB_TYPE=os.environ.get("DB_TYPE", "mariadb"),
        DB_HOST=os.environ.get("DB_HOST", "127.0.0.1"),
        DB_PORT=int(os.environ.get("DB_PORT", 3306)),
        DB_USER=os.environ.get("DB_USER", "root"),
        DB_PASSWORD=os.environ.get("DB_PASSWORD", "1234"),
        DB_NAME=os.environ.get("DB_NAME", "sentinel"),
        DATABASE_PATH=default_db_path,
        UPLOAD_FOLDER=default_upload_dir,
        MAX_CONTENT_LENGTH=32 * 1024 * 1024  # 32MB max file size
    )

    if test_config:
        app.config.update(test_config)
        # If test_config specifies DATABASE_PATH without explicit DB_TYPE, use sqlite
        if "DATABASE_PATH" in test_config and "DB_TYPE" not in test_config:
            app.config["DB_TYPE"] = "sqlite"

    # Ensure uploads directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # 1. Initialize Database connection and tables
    db_conn = DatabaseConnection(
        db_type=app.config.get("DB_TYPE", "mariadb"),
        host=app.config.get("DB_HOST", "127.0.0.1"),
        port=app.config.get("DB_PORT", 3306),
        user=app.config.get("DB_USER", "root"),
        password=app.config.get("DB_PASSWORD", "1234"),
        database=app.config.get("DB_NAME", "sentinel"),
        db_path=app.config.get("DATABASE_PATH")
    )
    db_conn.init_db()

    # 2. Instantiate Repositories (Data Access Layer)
    user_repository = SQLiteUserRepository(db_conn)
    incident_repository = SQLiteIncidentRepository(db_conn)
    comment_repository = SQLiteCommentRepository(db_conn)

    # 3. Instantiate Services (Business Logic Layer)
    preview_service = PreviewService()
    auth_service = AuthService(user_repo=user_repository)
    incident_service = IncidentService(
        incident_repo=incident_repository,
        comment_repo=comment_repository,
        preview_service=preview_service
    )

    # Attach service layer instances to app context for thin controller access
    app.auth_service = auth_service
    app.incident_service = incident_service

    # 4. Register Route Blueprints (Presentation / Web Layer)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(incident_bp)

    return app
