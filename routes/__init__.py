"""routes/__init__.py - Flask route registration for Clever.

Why: Provide the canonical implementation home for HTTP route registration so
     app.py can delegate endpoint wiring without owning every interface concern.
Where: Imported by app.py during runtime startup via register_routes(app).
How: Registers focused route modules in one deterministic place.
"""

from __future__ import annotations

from flask import Flask

from .cognitive import register_cognitive_routes
from .core import register_core_routes


def register_routes(app: Flask) -> None:
    """Register Clever's Flask routes.

    Why: Centralizes route wiring so interface ownership remains explicit and
         tests can verify endpoint availability after bootstrap changes.
    Where: Called from app.py after Flask app creation and configuration.
    How: Invokes each route module's registration function against the app.
    """
    register_core_routes(app)
    register_cognitive_routes(app)
