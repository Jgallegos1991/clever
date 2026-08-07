"""Persona loader contract tests.

Why: Ensure the PersonaLoader surfaces Jay's canonical persona blueprint with
     integrity metadata so runtime systems can trust the active persona.
Where: Executed with the rest of the test suite to guard against regressions in
       persona loading, caching, or path resolution logic.
How: Instantiate PersonaLoader, force a refresh to read from disk, verify the
     Infinite Navigator blueprint is present, and confirm cached reload keeps
     metadata consistent.
"""

from core.persona_loader import PersonaLoader


def test_persona_loader_reads_and_caches_blueprint():
    loader = PersonaLoader()
    document = loader.load(force_refresh=True)

    assert "Clever (The Infinite Navigator)" in document.text
    assert document.content_hash
    assert document.size_bytes > 0

    cached = loader.load(force_refresh=False)
    assert cached.content_hash == document.content_hash
    assert cached.modified_ts == document.modified_ts
    assert cached.path == document.path

    excerpt = loader.peek_excerpt(length=120)
    assert excerpt
