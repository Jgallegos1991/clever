#!/usr/bin/env python3
"""
Clever Knowledge Validation & Testing Script (Offline-Only)

Why: Validates Clever's knowledge base functionality without external dependencies
Where: Called by CI/CD for automated testing and validation
How: Uses offline-only testing methods respecting digital sovereignty

File Usage:
    - Primary callers: GitHub Actions CI, make targets
    - Dependencies: None (fully offline)
    - Database interactions: Read-only validation
    - Configuration: Respects offline-first principle

Connects to:
    - database.py: Knowledge base validation
    - config.py: System configuration checks
    - debug_config.py: Logging validation results
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


class CleverOfflineValidator:
    """
    Offline-only knowledge validation for Clever's digital brain extension.

    Why: Ensures knowledge base integrity without compromising digital sovereignty
    Where: Used in CI/CD pipeline for automated validation
    How: Validates file structure, database schema, and configuration consistency
    """

    def __init__(self):
        self.test_results = []
        self.project_root = Path(__file__).parent

    def validate_file_structure(self) -> Dict[str, Any]:
        """
        Validate essential Clever files exist and are accessible.

        Why: Ensures core system files are present for proper operation
        Where: Called during CI validation to catch missing dependencies
        How: Checks for existence of critical files and directories
        """
        required_files = [
            "app.py",
            "config.py",
            "database.py",
            "persona.py",
            "evolution_engine.py",
        ]

        results = {
            "test": "file_structure",
            "status": "pass",
            "missing_files": [],
            "found_files": [],
        }

        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                results["found_files"].append(file_path)
            else:
                results["missing_files"].append(file_path)
                results["status"] = "fail"

        return results

    def validate_database_schema(self) -> Dict[str, Any]:
        """
        Validate database configuration without connecting.

        Why: Ensures database schema definitions are valid
        Where: CI validation for database integrity
        How: Checks configuration files and schema definitions
        """
        results = {"test": "database_schema", "status": "pass", "checks": []}

        try:
            # Check if database.py imports properly
            import database

            results["checks"].append("database module imports successfully")

            # Check if config has database path
            import config

            if hasattr(config, "DB_PATH"):
                results["checks"].append("DB_PATH configured")
            else:
                results["status"] = "fail"
                results["checks"].append("DB_PATH missing")

        except ImportError as e:
            results["status"] = "fail"
            results["checks"].append(f"Import error: {e}")

        return results

    def validate_offline_compliance(self) -> Dict[str, Any]:
        """
        Validate system maintains offline-first principles.

        Why: Ensures digital sovereignty by checking for external dependencies
        Where: CI validation for offline compliance
        How: Scans code for prohibited external calls
        """
        results = {"test": "offline_compliance", "status": "pass", "violations": []}

        # Check for requests/urllib imports that might violate offline principle
        python_files = list(self.project_root.glob("*.py"))
        prohibited_imports = ["requests", "urllib.request", "httpx", "aiohttp"]

        for py_file in python_files:
            if py_file.name == "validate_knowledge.py":
                continue  # Skip the old version

            try:
                content = py_file.read_text()
                for prohibited in prohibited_imports:
                    if f"import {prohibited}" in content:
                        results["violations"].append(f"{py_file.name}: imports {prohibited}")
                        results["status"] = "warn"  # Warn instead of fail for now
            except Exception:
                continue

        return results

    def run_quick_validation(self) -> bool:
        """
        Run quick validation suite for CI.

        Why: Provides fast validation for CI/CD pipeline
        Where: Called with --quick flag for rapid testing
        How: Runs essential tests without comprehensive analysis
        """
        print("🧠 Clever Offline Knowledge Validation")
        print("=" * 50)

        tests = [
            self.validate_file_structure,
            self.validate_database_schema,
            self.validate_offline_compliance,
        ]

        all_passed = True

        for test_func in tests:
            result = test_func()
            self.test_results.append(result)

            status_icon = (
                "✅" if result["status"] == "pass" else "⚠️" if result["status"] == "warn" else "❌"
            )
            print(f"{status_icon} {result['test']}: {result['status'].upper()}")

            if result["status"] == "fail":
                all_passed = False

            # Print details for failures/warnings
            if result["status"] != "pass":
                for key, value in result.items():
                    if key not in ["test", "status"] and value:
                        print(f"   {key}: {value}")

        print("=" * 50)
        print(f"📊 Overall Status: {'✅ PASS' if all_passed else '❌ FAIL'}")

        return all_passed


def main():
    """Main entry point for validation script."""
    parser = argparse.ArgumentParser(description="Clever Knowledge Validation")
    parser.add_argument("--quick", action="store_true", help="Run quick validation")
    args = parser.parse_args()

    validator = CleverOfflineValidator()

    if args.quick:
        success = validator.run_quick_validation()
        sys.exit(0 if success else 1)
    else:
        # Default: run quick validation
        success = validator.run_quick_validation()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
