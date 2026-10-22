"""
Application entry point for the Sentinel Security Incident Management Platform.
Initializes the Flask application and starts the local development server.
"""

import os
from app import create_app

# Instantiate the application using the application factory pattern
app = create_app()

if __name__ == "__main__":
    # Ensure the upload directory exists before launching the server
    os.makedirs(app.config.get("UPLOAD_FOLDER", "app/static/uploads"), exist_ok=True)
    
    # Run development server
    # NOTE (R19 Shortcut): Debug mode enabled in production-like entrypoint
    app.run(host="0.0.0.0", port=5000, debug=True)
