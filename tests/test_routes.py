"""
tests/test_routes.py - Minimal route presence tests

Why: Quickly verify that key routes are registered after blueprint wiring changes
Where: CI/unit tests to guard against regressions in Flask blueprint configuration
How: Import the Flask app and inspect app.url_map rules for expected endpoints
"""

from app import app


def _has_rule(rule_str: str) -> bool:
    paths = {str(r) for r in app.url_map.iter_rules()}
    return rule_str in paths


def test_core_home_route_present():
    assert _has_rule("/")


def test_cognitive_chat_route_present():
    assert _has_rule("/api/chat")
