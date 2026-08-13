"""Cognition subsystem package for Clever.

Why: Establish cognition/ as the canonical package boundary for NLP, academic
     knowledge, introspection, and other cognition-owned runtime responsibilities.
Where: Imported by active runtime modules using canonical package paths such as
       cognition.nlp_processor and cognition.academic_knowledge_engine.
How: Keep this package marker lightweight; export concrete APIs from their owning
     modules rather than recreating root-level aliases.
"""
