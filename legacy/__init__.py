"""Legacy compatibility package for Clever.

Why: Enables legacy module imports to work when legacy files are referenced from modern
     runtime paths.
Where: Provides package-level access for legacy/ modules that were moved from root.
How: Exposes the legacy folder as a Python package so imports like
     legacy.clever_ultimate_capabilities work consistently.
"""

__all__ = [
    "clever_ultimate_capabilities",
]
