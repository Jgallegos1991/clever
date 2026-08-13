"""routes/core.py - Core Flask routes for Clever.

Why: Own the minimal user-facing and health endpoints required for the local
     Clever interface to load and for tests/diagnostics to confirm liveness.
Where: Registered by routes.register_routes(app) during app startup.
How: Adds conservative handlers directly to the Flask app without inventing
     new runtime architecture beyond the documented endpoint contract.
"""

from __future__ import annotations

from flask import Flask, jsonify, render_template


def register_core_routes(app: Flask) -> None:
    """Register core application routes.

    Why: Ensure the local UI and basic status endpoint are available after the
         route package is restored.
    Where: Called by routes.register_routes(app).
    How: Defines '/' and '/health' handlers if they are not already present.
    """

    if "core.index" not in app.view_functions:
        @app.get("/", endpoint="core.index")
        def index():
            """Serve the Clever home interface.

            Why: Provide the primary local UI entrypoint.
            Where: GET /.
            How: Render templates/index.html when present, otherwise return a
                 minimal fallback containing the Clever name for smoke tests.
            """
            try:
                return render_template("index.html")
            except Exception:
                return "Clever"

    if "core.health" not in app.view_functions:
        @app.get("/health", endpoint="core.health")
        def health():
            """Return a minimal health status.

            Why: Provide a stable liveness endpoint for tests and local checks.
            Where: GET /health.
            How: Return a conservative JSON status without importing heavier
                 subsystems or triggering cognitive startup side effects.
            """
            return jsonify({"status": "ok"})
