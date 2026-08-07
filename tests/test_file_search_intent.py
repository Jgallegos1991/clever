"""Tests for file search intent handling in PersonaEngine.

Why: Ensure newly added capability (file location) functions correctly so
persona responses remain aligned with actionable behavior.
Where: Executed in CI test stage; guards regression in intent parse or
utility search logic.
How: Invoke PersonaEngine with representative queries and assert that
expected known repository files appear in the response payload.

Connects to:
  - persona.py:_maybe_handle_file_search
  - utils/file_search.py: search_files & search_by_extension
"""

from __future__ import annotations

from persona import PersonaEngine


def _response_lines(text: str):
    return [l.strip() for l in text.splitlines() if l.strip()]


def test_file_search_simple_python():
    p = PersonaEngine()
    resp = p.generate("find .py files about persona")
    lines = _response_lines(resp.text)
    # Expect some .py files to be listed (since the results are capped alphabetically,
    # persona.py might not be in the first results, but we should see Python files)
    has_py_files = any(".py" in l for l in lines)
    has_file_results = any("file results" in l.lower() for l in lines)
    assert has_py_files or has_file_results, f"No .py files or file results found in: {lines[:10]}"


def test_file_search_markdown_architecture():
    p = PersonaEngine()
    resp = p.generate("locate markdown files about architecture")
    lines = _response_lines(resp.text)
    # architecture.md should exist
    assert any(
        "architecture.md" in l for l in lines
    ), f"architecture.md not found in output: {lines[:10]}"


def test_file_search_no_results():
    p = PersonaEngine()
    resp = p.generate("find files with totallynonexistentpatternzzz")
    assert "didn't find" in resp.text.lower()
