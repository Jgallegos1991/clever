"""Memory subsystem package for Clever.

Why: Establish memory/ as the canonical package boundary for memory-owned runtime
     responsibilities.
Where: Imported by active runtime modules using canonical package paths such as
       memory.memory_engine.
How: Keep this package marker lightweight; export concrete APIs from their owning
     modules rather than recreating root-level aliases.
"""
