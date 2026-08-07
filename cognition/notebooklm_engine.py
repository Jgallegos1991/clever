"""
notebooklm_engine.py - Minimal Document Analysis System

Why: Provides basic document analysis for Clever's knowledge system
Where: Integrates with database for document storage  
How: Simple document processing without complex dependencies
"""

import sqlite3
from typing import Any, Dict, List, Optional

import config
from database import DatabaseManager
from debug_config import get_debugger


class NotebookLMEngine:
    """
    Minimal Document Analysis Engine

    Why: Provides basic document analysis capabilities for Clever
    Where: Called by memory system for document processing
    How: Simple analysis without heavy ML dependencies
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize with basic database connection"""
        self.db_path = db_path or config.DB_PATH
        self.db = DatabaseManager(self.db_path)
        self.debugger = get_debugger()

        # Initialize basic schema
        self._init_schema()

    def _init_schema(self):
        """Initialize minimal document analysis schema"""
        with self.db._lock, self.db._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS document_analysis (
                    source_id INTEGER PRIMARY KEY,
                    word_count INTEGER,
                    summary TEXT,
                    created_at REAL,
                    FOREIGN KEY (source_id) REFERENCES sources(id)
                )
            """
            )
            conn.commit()

    def analyze_document(
        self, source_id: int, force_reprocess: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Basic document analysis"""
        try:
            with self.db._lock, self.db._connect() as conn:
                cursor = conn.execute(
                    "SELECT id, filename, content FROM sources WHERE id = ?",
                    (source_id,),
                )
                row = cursor.fetchone()

            if not row:
                return None

            doc_id, filename, content = row
            word_count = len(content.split())
            summary = content[:200] + "..." if len(content) > 200 else content

            # Store analysis
            with self.db._lock, self.db._connect() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO document_analysis 
                    (source_id, word_count, summary, created_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (doc_id, word_count, summary, 1000),
                )
                conn.commit()

            return {
                "doc_id": doc_id,
                "filename": filename,
                "word_count": word_count,
                "summary": summary,
            }

        except Exception as e:
            self.debugger.error("noteboomlm.analyze_document", f"Analysis failed: {e}")
            return None

    def query_documents(self, query: str, max_sources: int = 10) -> List[Dict[str, Any]]:
        """
        Query documents based on search terms

        Why: Provides document search functionality
        Where: Called by app.py query_documents endpoint
        How: Simple text matching in document content
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT doc_id, summary, word_count FROM document_analysis 
                    WHERE summary LIKE ? 
                    LIMIT ?
                """,
                    (f"%{query}%", max_sources),
                )

                results = []
                for row in cursor:
                    results.append(
                        {
                            "doc_id": row[0],
                            "summary": row[1],
                            "word_count": row[2],
                            "relevance_score": 0.5,  # Simple placeholder
                        }
                    )
                return results
        except Exception as e:
            self.debugger.error("notebooklm.query_documents", f"Query failed: {e}")
            return []

    def find_cross_document_connections(self, source_id: int) -> List[Dict[str, Any]]:
        """
        Find connections between documents

        Why: Identifies relationships between documents
        Where: Called by app.py find_connections endpoint
        How: Simple keyword matching between documents
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get source document summary
                cursor = conn.execute(
                    "SELECT summary FROM document_analysis WHERE doc_id = ?",
                    (source_id,),
                )
                source_row = cursor.fetchone()
                if not source_row:
                    return []

                source_summary = source_row[0]
                # Simple connection based on shared keywords
                connections = []
                cursor = conn.execute(
                    "SELECT doc_id, summary FROM document_analysis WHERE doc_id != ?",
                    (source_id,),
                )

                for row in cursor:
                    # Very simple connection scoring
                    shared_words = len(set(source_summary.split()) & set(row[1].split()))
                    if shared_words > 3:
                        connections.append(
                            {
                                "doc_id": row[0],
                                "connection_strength": shared_words / 10.0,
                                "connection_type": "keyword_overlap",
                            }
                        )

                return connections[:5]  # Return top 5 connections
        except Exception as e:
            self.debugger.error("notebooklm.find_connections", f"Connection search failed: {e}")
            return []

    def generate_collection_overview(self, focus_topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate overview of document collection

        Why: Provides high-level insights into document collection
        Where: Called by app.py collection_overview endpoint
        How: Aggregates statistics and identifies key themes
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT COUNT(*), AVG(word_count), SUM(word_count) 
                    FROM document_analysis
                """
                )
                stats = cursor.fetchone()

                # Get sample summaries for theme detection
                cursor = conn.execute("SELECT summary FROM document_analysis LIMIT 10")
                # summaries available for future theme detection

                overview = {
                    "total_documents": stats[0] or 0,
                    "average_length": int(stats[1]) if stats[1] else 0,
                    "total_words": stats[2] or 0,
                    "key_themes": ["analysis", "research", "knowledge"],  # Placeholder
                    "focus_topic": focus_topic,
                    "collection_health": "good" if stats[0] > 0 else "empty",
                }

                return overview
        except Exception as e:
            self.debugger.error("notebooklm.generate_overview", f"Overview generation failed: {e}")
            return {
                "total_documents": 0,
                "average_length": 0,
                "total_words": 0,
                "key_themes": [],
                "focus_topic": focus_topic,
                "collection_health": "error",
            }


# Global instance
_notebooklm_engine = None


def get_notebooklm_engine() -> NotebookLMEngine:
    """
    Get global NotebookLM engine instance

    Why: Provides singleton access to document analysis capabilities
    Where: Used by app.py and other modules needing document analysis
    How: Creates engine on first access, reuses for subsequent calls
    """
    global _notebooklm_engine
    if _notebooklm_engine is None:
        _notebooklm_engine = NotebookLMEngine()
    return _notebooklm_engine
