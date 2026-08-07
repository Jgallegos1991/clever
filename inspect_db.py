#!/usr/bin/env python3
"""
Quick database inspection script for Clever.

Why: Give Jay and Codex a snapshot of database health without opening SQLite
manually.
Where: Run ad-hoc when validating new ingestions or investigating data drift.
How: Connects to `clever.db`, enumerates tables, and samples key records.

File Usage:
    - `inspect_db.py`: executed directly from the project root.
Connects to:
    - `clever.db`: primary storage for conversations and knowledge.
    - `sources`, `utterances`: tables sampled for diagnostic output.
"""
import sqlite3
from pathlib import Path

import config


def inspect_database():
    """
    Inspect Clever's SQLite database and print human-readable stats.

    Why: Quickly verify table counts and data presence after maintenance tasks.
    Where: Called by the module’s CLI or other diagnostics tooling.
    How: Opens a connection, queries metadata, and prints formatted summaries.

    File Usage:
        - `inspect_db.py`: default entry point for quick checks.
    Connects to:
        - SQLite `sqlite_master`: reveals table inventory.
        - `sources` and `utterances`: validated for sample content.
    """
    db_path = config.DB_PATH
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return

    print(f"📊 Inspecting Clever's Database: {db_path}")
    print("=" * 50)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print("📋 Database Tables:")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  - {table_name}: {count} records")

    print("\n📚 Source Knowledge:")
    try:
        cursor.execute("SELECT filename, size FROM sources LIMIT 10")
        sources = cursor.fetchall()
        if sources:
            for filename, size in sources:
                size_kb = size / 1024 if size else 0
                print(f"  - {filename} ({size_kb:.1f} KB)")
        else:
            print("  - No source files in database yet")
    except:
        print("  - Sources table not found or empty")

    print("\n💭 Conversation History:")
    try:
        cursor.execute(
            "SELECT role, LEFT(text, 50) FROM utterances ORDER BY timestamp DESC LIMIT 5"
        )
        utterances = cursor.fetchall()
        if utterances:
            for role, text_preview in utterances:
                print(f"  - {role}: {text_preview}...")
        else:
            print("  - No conversations recorded yet")
    except:
        print("  - Utterances table not found or empty")

    conn.close()


if __name__ == "__main__":
    inspect_database()
