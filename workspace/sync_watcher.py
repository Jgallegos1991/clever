import time

#!/usr/bin/env python3
"""
Clever Sync Watcher - Monitors sync directories for changes and triggers ingestion

This script watches the Clever_Sync and synaptic_hub_sync directories for file changes
and automatically triggers ingestion when new files are detected.

Usage:
    python sync_watcher.py

Environment Variables:
    CLEVER_SYNC_DIR: Path to Clever_Sync directory (default: ./Clever_Sync)
    SYNAPTIC_HUB_SYNC_DIR: Path to synaptic_hub_sync directory (default: ./synaptic_hub_sync)
    FLASK_URL: Flask server URL (default: http://localhost:5000)
"""


import logging
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import config

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SyncEventHandler(FileSystemEventHandler):
    """File system event handler for automatic ingestion of sync directory changes.

    Why: Enables real-time processing of files added to sync directories,
        ensuring Clever AI's knowledge base stays current with external changes.
    Where: Used by the sync watcher system to monitor Clever_Sync and
         synaptic_hub_sync directories for file system events.
    How: Inherits from FileSystemEventHandler, debounces events to prevent
        rapid-fire ingestion, and directly uses FileIngestor for processing.

    Connects to:
        - file_ingestor.py:
            - `__init__()`: Creates an instance of `FileIngestor`.
            - `trigger_ingestion()`: Calls `self.ingestor.ingest_file()` to process the changed file.
        - config.py:
            - `main()`: Reads `config.SYNC_DIR` and `config.SYNAPTIC_HUB_DIR` to determine which directories to monitor.
            - `SyncEventHandler.__init__()`: The `FileIngestor` it creates is initialized with `config.SYNC_DIR`.
    """

    def __init__(self):
        """Initialize sync event handler with debouncing + FileIngestor.

        Why: Prevent repeated rapid ingestion and centralize ingestion logic.
        Where: Constructed in main() when watcher starts.
        How: Sets timestamp, debounce interval, and instantiates FileIngestor.
        """
        self.last_trigger = 0
        self.debounce_seconds = 2  # Prevent rapid-fire ingestion
        # Lazy import to avoid circulars during certain test contexts
        from file_ingestor import FileIngestor  # local import by design

        self.ingestor = FileIngestor(base_dir=config.SYNC_DIR)

    def on_any_event(self, event):
        """Process filesystem events with debouncing and filtering."""
        if event.is_directory:
            return
        # Debounce rapid events
        current_time = time.time()
        if current_time - self.last_trigger < self.debounce_seconds:
            return
        self.last_trigger = current_time
        src = Path(event.src_path)
        if _should_ignore_path(src):
            return
        if not _is_allowed_path(src):
            logger.debug("Skipping non-canonical path: %s", src)
            return
        logger.info(f"File change detected: {src}")
        # Trigger direct ingestion
        self.trigger_ingestion(str(src))

    def trigger_ingestion(self, file_path):
        """Trigger ingestion endpoint on Flask server"""
        """
        Execute direct file ingestion with comprehensive error handling.
        
        Why: Processes detected file changes immediately to keep Clever AI's
             knowledge base synchronized with external file updates.
        Where: Called by on_any_event after successful event filtering and
               debouncing validation.
        How: Uses FileIngestor to process the file, logs ingestion status,
             and handles any processing errors gracefully with detailed logging.
        
        Args:
            file_path: Path to the file that triggered the ingestion event
        """
        try:
            status = self.ingestor.ingest_file(file_path)
            if status in ("inserted", "updated"):
                logger.info(f"Ingestion {status} for {file_path}")
            else:
                logger.info(f"No ingestion needed for {file_path} (status: {status})")
        except Exception as e:
            logger.error(f"Error during ingestion of {file_path}: {e}")


def _allowed_ingest_roots() -> list[Path]:
    """Return the canonical directories approved for ingestion.

    Why: Prevents ingestion from tool/config/virtualenv folders and enforces
         a strict allowlist of Clever content roots.
    Where: Used by _is_allowed_path and watcher setup.
    How: Resolves configured sync roots into absolute Paths.
    """
    roots = []
    for root in (config.SYNC_DIR, config.SYNAPTIC_HUB_DIR):
        try:
            roots.append(Path(root).expanduser().resolve())
        except Exception:
            continue
    return roots


_DISALLOWED_DIR_NAMES = {
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    "node_modules",
    ".codex",
    "site-packages",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".eggs",
    ".cache",
    "logs",
    "backups",
    "ipfs_repo",
    "legacy",
    "experiments",
    ".state",
}

_DISALLOWED_FILE_MARKERS = (".tmp", ".swp", "~", ".DS_Store")


def _should_ignore_path(path: Path) -> bool:
    """Check whether a path should be ignored by the sync watcher.

    Why: Avoids ingesting files from virtualenvs, hidden folders, tool/config
         directories, and transient artifacts.
    Where: Used by SyncEventHandler before ingestion.
    How: Rejects paths containing hidden or disallowed directory names and
         file markers.
    """
    parts = path.parts
    for part in parts:
        if part.startswith("."):
            return True
        if part in _DISALLOWED_DIR_NAMES:
            return True
    path_str = str(path)
    return any(marker in path_str for marker in _DISALLOWED_FILE_MARKERS)


def _is_allowed_path(path: Path) -> bool:
    """Return True if the path is within canonical ingestion roots."""
    resolved = path.expanduser().resolve()
    for root in _allowed_ingest_roots():
        try:
            resolved.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def _resolve_watch_directories() -> list[Path]:
    """Determine directories that should be monitored for changes."""
    sync_dirs: list[Path] = []

    clever_path = Path(config.SYNC_DIR)
    if clever_path.exists():
        sync_dirs.append(clever_path)
        logger.info(f"Watching Clever_Sync: {clever_path.absolute()}")
    else:
        logger.warning(f"Clever_Sync directory not found: {clever_path.absolute()}")

    synaptic_path = Path(config.SYNAPTIC_HUB_DIR)
    if synaptic_path.exists():
        sync_dirs.append(synaptic_path)
        logger.info(f"Watching synaptic_hub_sync: {synaptic_path.absolute()}")
    else:
        logger.warning(f"synaptic_hub_sync directory not found: {synaptic_path.absolute()}")

    if not sync_dirs:
        logger.error("No sync directories found. Creating Clever_Sync directory...")
        clever_path.mkdir(parents=True, exist_ok=True)
        sync_dirs.append(clever_path)
        logger.info(f"Created and watching: {clever_path.absolute()}")

    return sync_dirs


def start_watchers() -> Observer:
    """Start filesystem observers for configured directories."""
    sync_dirs = _resolve_watch_directories()
    event_handler = SyncEventHandler()
    observer = Observer()
    for watch_dir in sync_dirs:
        observer.schedule(event_handler, str(watch_dir), recursive=True)
    observer.start()
    logger.info("Sync watcher started.")
    return observer


def main():
    """
    Initialize and run the sync directory monitoring system.

    Why: Provides continuous monitoring of sync directories to enable
         real-time knowledge base updates for Clever AI's offline-first architecture.
    Where: Entry point for the sync watcher service, typically run as a
           background process or daemon.
    How: Configures directory paths from environment, validates existence,
         sets up watchdog Observer with SyncEventHandler, and runs monitoring loop.
    """

    observer = start_watchers()
    logger.info("Sync watcher running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping sync watcher...")
        observer.stop()

    observer.join()
    logger.info("Sync watcher stopped.")


if __name__ == "__main__":
    main()
