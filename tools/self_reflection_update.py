#!/usr/bin/env python3
"""
Automates Clever's self-reflection workflow.

Why: Preserve longitudinal awareness so Clever tracks her evolution, insights,
and architectural drift without relying on external memory.
Where: Triggered manually by Jay or automated maintenance jobs when compiling
daily audits, then referenced in `logs/self_reflection_reports/`.
How: Regenerates manifest artifacts, updates cognitive maps, records telemetry
in the evolution engine, and writes narrative reports.

File Usage:
    - `tools/self_reflection_update.py`: direct CLI entry for the workflow.
    - `automation scripts`: import helper functions when batching updates.
Connects to:
    - `CLEVER_MANIFEST.md`: regenerated manifesto of current capabilities.
    - `Clever_Cognitive_Map.dot`: visual knowledge graph rendered post-run.
    - `evolution_engine.py`: logs telemetry for long-term trend analysis.

Features:
    - Regenerates CLEVER_MANIFEST.md (extended summaries) and the cognitive map.
    - Records each run in evolution and memory engines for long-term awareness.
    - Writes a daily Markdown report under logs/self_reflection_reports/.
    - Maintains historical metrics and renders cumulative trend charts.
    - Commits the updated artifacts and can optionally push upstream.
"""

from __future__ import annotations

import ast
import io
import json
import os
import subprocess
import sys
import time
import tokenize
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:  # Headless plotting backend for report charts
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    _MATPLOTLIB_AVAILABLE = True
    _MATPLOTLIB_ERROR: Optional[str] = None
except Exception as exc:  # pragma: no cover - optional dependency
    plt = None  # type: ignore
    _MATPLOTLIB_AVAILABLE = False
    _MATPLOTLIB_ERROR = str(exc)

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MANIFEST_PATH = REPO_ROOT / "CLEVER_MANIFEST.md"
COGNITIVE_MAP_PATH = REPO_ROOT / "Clever_Cognitive_Map.dot"
ARCHITECTURE_PATH = REPO_ROOT / "CLEVER_ARCHITECTURE_OVERVIEW.md"

LOG_DIR = REPO_ROOT / "logs"
REPORT_DIR = LOG_DIR / "self_reflection_reports"
HISTORY_PATH = REPORT_DIR / "history.json"
LINE_CHART_PATH = REPORT_DIR / "line_counts.png"
FILETYPE_CHART_PATH = REPORT_DIR / "file_type_trends.png"
LAST_IPFS_PATH = REPORT_DIR / "last_ipfs_cids.json"

SKIP_DIRS: Set[str] = {
    "__pycache__",
    "node_modules",
    "venv",
    "venvs",
    ".venv",
    "coqui_env",
    "venv_tts",
    "logs",
    "models",
    ".git",
}

DOCSTRING_LIMIT_LINES = 100
SUMMARY_MAX_LENGTH = 300

try:
    from evolution_engine import get_evolution_engine

    _EVOLUTION_AVAILABLE = True
    _EVOLUTION_IMPORT_ERROR: Optional[str] = None
except Exception as exc:  # pragma: no cover - defensive
    get_evolution_engine = None  # type: ignore
    _EVOLUTION_AVAILABLE = False
    _EVOLUTION_IMPORT_ERROR = str(exc)

try:
    from memory_engine import MemoryContext, get_memory_engine

    _MEMORY_AVAILABLE = True
    _MEMORY_IMPORT_ERROR: Optional[str] = None
except Exception as exc:  # pragma: no cover - defensive
    get_memory_engine = None  # type: ignore
    MemoryContext = None  # type: ignore
    _MEMORY_AVAILABLE = False
    _MEMORY_IMPORT_ERROR = str(exc)


def is_binary(path: Path) -> bool:
    """Detect binary files via null-byte sampling."""
    try:
        with path.open("rb") as handle:
            chunk = handle.read(2048)
    except OSError:
        return True
    return b"\x00" in chunk


def count_lines(path: Path) -> int:
    """Count lines in binary-safe mode."""
    try:
        with path.open("rb") as handle:
            line_count = 0
            last_char = None
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                if not chunk:
                    break
                line_count += chunk.count(b"\n")
                last_char = chunk[-1]
            if last_char is not None and last_char != 0x0A:
                line_count += 1
            return line_count
    except OSError:
        return 0


def extract_summary(path: Path) -> str:
    """Build a summary from docstrings/comments within the first 100 lines."""
    if is_binary(path):
        return "Binary or unreadable file."

    lines: List[str] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for _ in range(DOCSTRING_LIMIT_LINES):
                line = handle.readline()
                if not line:
                    break
                lines.append(line.rstrip("\n"))
    except OSError:
        return "Binary or unreadable file."

    if not lines:
        return "Empty file."

    text = "\n".join(lines)
    docstrings: List[str] = []
    comments: List[str] = []

    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            token_type, token_string, *_ = token
            if token_type == tokenize.STRING:
                cleaned = token_string
                try:
                    literal = ast.literal_eval(token_string)
                    if isinstance(literal, bytes):
                        literal = literal.decode("utf-8", errors="replace")
                    cleaned = str(literal)
                except Exception:
                    cleaned = token_string.strip("\"'")
                docstrings.append(cleaned)
            elif token_type == tokenize.COMMENT:
                stripped = token_string.lstrip("#").strip()
                if stripped:
                    comments.append(stripped)
    except (tokenize.TokenError, IndentationError):
        pass

    components = [" ".join(value.split()) for value in docstrings if value.strip()]
    components.extend(" ".join(value.split()) for value in comments if value.strip())

    summary_text = " ".join(components)

    if not summary_text:
        for line in lines:
            stripped = line.strip()
            if stripped:
                summary_text = stripped
                break

    if not summary_text:
        summary_text = "No descriptive content in top lines."

    summary_text = " ".join(summary_text.split())
    if len(summary_text) > SUMMARY_MAX_LENGTH:
        summary_text = summary_text[: SUMMARY_MAX_LENGTH - 3] + "..."
    if not summary_text.endswith("."):
        summary_text += "."

    return summary_text.replace("|", r"\|")


def should_skip(path: Path) -> bool:
    """Determine whether path resides in a skipped directory."""
    return any(part in SKIP_DIRS for part in path.parts)


def format_manifest_row(rel_path: str, modified: str, line_count: int, summary: str) -> str:
    return f"| {rel_path} | {modified} | {line_count} | {summary} |"


def _build_manifest_stats(
    entries: List[Dict[str, object]], generated_iso: str
) -> Dict[str, object]:
    suffix_counter: Counter[str] = Counter()
    total_lines = 0

    for entry in entries:
        suffix = entry.get("suffix_label", "")
        suffix_counter[str(suffix)] += 1
        total_lines += int(entry.get("line_count", 0))

    stats: Dict[str, object] = {
        "generated": generated_iso,
        "total_files": len(entries),
        "total_line_count": total_lines,
        "recent_files": [],
        "top_suffixes": list(suffix_counter.most_common(5)),
        "suffix_counts": dict(suffix_counter),
        "python_files": suffix_counter.get("py", 0),
        "markdown_files": suffix_counter.get("md", 0),
        "notebook_files": suffix_counter.get("ipynb", 0),
    }

    recent_files = sorted(
        entries,
        key=lambda entry: entry.get("modified_dt", datetime.min),
        reverse=True,
    )[:3]
    stats["recent_files"] = [
        {"path": entry.get("path"), "modified": entry.get("modified")} for entry in recent_files
    ]

    return stats


def _build_manifest_summary(entries: List[Dict[str, object]], stats: Dict[str, object]) -> str:
    generated_iso = stats.get("generated") or datetime.now().isoformat()
    total_files = stats.get("total_files", 0)
    total_lines = stats.get("total_line_count", 0)

    if not entries:
        return f"Manifest refresh at {generated_iso} found no files to record."

    top_suffixes = stats.get("top_suffixes", [])
    suffix_snippet = ", ".join(f"{suffix}:{count}" for suffix, count in top_suffixes[:3])
    recent_files = stats.get("recent_files", [])
    recent_snippet = ", ".join(
        f"{item.get('path')} @ {item.get('modified')}" for item in recent_files if item.get("path")
    )

    summary = (
        f"Manifest refresh at {generated_iso} captured {total_files} files "
        f"spanning {total_lines} lines. Top types: {suffix_snippet or 'n/a'}. "
        f"Recent updates: {recent_snippet or 'none listed'}."
    )
    return summary


def generate_manifest() -> Tuple[bool, str, Dict[str, object]]:
    """Regenerate CLEVER_MANIFEST.md; return (changed, summary, stats)."""
    entries: List[Dict[str, object]] = []

    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(REPO_ROOT)
        if should_skip(relative):
            continue
        if path.resolve() == MANIFEST_PATH.resolve():
            continue
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue

        rel_path = relative.as_posix()
        modified_dt = datetime.fromtimestamp(stat.st_mtime)
        modified = modified_dt.isoformat()
        line_count = count_lines(path)
        summary = extract_summary(path)
        suffix = Path(rel_path).suffix.lower()
        suffix_label = suffix[1:] if suffix.startswith(".") else (suffix or "no_ext")

        entries.append(
            {
                "path": rel_path,
                "modified": modified,
                "modified_dt": modified_dt,
                "line_count": line_count,
                "summary": summary,
                "suffix_label": suffix_label,
            }
        )

    entries.sort(key=lambda item: item["path"])

    generated = datetime.now().isoformat()
    stats = _build_manifest_stats(entries, generated)
    manifest_summary = _build_manifest_summary(entries, stats)

    lines_out = [
        "# Clever Workspace Manifest",
        "",
        f"Generated on {generated}",
        "",
        "| Path | Last Modified | Line Count | Summary |",
        "| --- | --- | --- | --- |",
    ]

    for entry in entries:
        lines_out.append(
            format_manifest_row(
                str(entry["path"]),
                str(entry["modified"]),
                int(entry["line_count"]),
                str(entry["summary"]),
            )
        )

    manifest_modified = datetime.now().isoformat()
    manifest_line_count = len(lines_out) + 1
    manifest_footer_summary = "Clever Workspace Manifest with extended summaries."
    lines_out.append(
        format_manifest_row(
            "CLEVER_MANIFEST.md",
            manifest_modified,
            manifest_line_count,
            manifest_footer_summary,
        )
    )

    new_content = "\n".join(lines_out) + "\n"
    existing = ""
    if MANIFEST_PATH.exists():
        existing = MANIFEST_PATH.read_text(encoding="utf-8", errors="replace")

    if existing == new_content:
        return False, manifest_summary, stats

    MANIFEST_PATH.write_text(new_content, encoding="utf-8")
    return True, manifest_summary, stats


def parse_architecture() -> Dict[str, Dict[str, str]]:
    """Parse CLEVER_ARCHITECTURE_OVERVIEW.md into subsystem text blocks."""
    if not ARCHITECTURE_PATH.exists():
        raise FileNotFoundError(
            "CLEVER_ARCHITECTURE_OVERVIEW.md is required to generate the cognitive map."
        )

    lines = ARCHITECTURE_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    subsystems: Dict[str, Dict[str, str]] = {}
    current = None
    collector: List[str] = []

    def commit():
        if current is not None:
            subsystems[current]["text"] = "\n".join(collector)

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("### "):
            commit()
            current = line[4:].strip()
            subsystems[current] = {"description": "", "text": ""}
            collector = []
            if i + 1 < len(lines) and lines[i + 1].strip():
                desc = lines[i + 1].strip()
                subsystems[current]["description"] = desc
                collector.append(desc)
                i += 1
        elif current is not None and line.strip():
            collector.append(line.strip())
        i += 1
    commit()

    return subsystems


def generate_cognitive_map() -> bool:
    """Rebuild Clever_Cognitive_Map.dot; return True if file changed."""
    subsystems = parse_architecture()
    if not subsystems:
        raise RuntimeError("No subsystems detected in CLEVER_ARCHITECTURE_OVERVIEW.md.")

    keyword_map: Dict[str, Iterable[str]] = {
        "Conversation Engine": ("conversation", "persona", "dialog", "nlp", "response"),
        "Voice & Audio": ("voice", "speech", "audio", "tts", "loop"),
        "Evolution & Adaptation": (
            "evolution",
            "adapt",
            "learning",
            "growth",
            "evolve",
        ),
        "Memory & Context": ("memory", "context", "recall", "history", "sync"),
        "Cognitive Intelligence": ("cognitive", "analysis", "insight", "intelligence"),
        "Knowledge & Learning": (
            "knowledge",
            "ingest",
            "document",
            "research",
            "context",
        ),
        "User Interface & Experience": (
            "interface",
            "route",
            "dashboard",
            "endpoint",
            "ui",
        ),
        "Validation & Testing": ("test", "validation", "suite", "regression"),
        "Monitoring & Operations": (
            "monitor",
            "health",
            "telemetry",
            "debug",
            "operations",
        ),
        "Supporting Infrastructure": ("infrastructure", "tool", "automation", "script"),
    }

    node_styles: Dict[str, Tuple[str, str]] = {
        "Conversation Engine": ("#8dd3c7", "Conversation Engine"),
        "Voice & Audio": ("#fb8072", "Voice & Audio"),
        "Evolution & Adaptation": ("#80b1d3", "Evolution & Adaptation"),
        "Memory & Context": ("#bebada", "Memory & Context"),
        "Cognitive Intelligence": ("#fdb462", "Cognitive Intelligence"),
        "Knowledge & Learning": ("#b3de69", "Knowledge & Learning"),
        "User Interface & Experience": ("#fccde5", "UI & Experience"),
        "Validation & Testing": ("#d9d9d9", "Validation & Testing"),
        "Monitoring & Operations": ("#bc80bd", "Monitoring & Ops"),
        "Supporting Infrastructure": ("#ccebc5", "Infrastructure"),
    }

    edges: Dict[Tuple[str, str], Set[str]] = {}

    for src, data in subsystems.items():
        text_blob = (data.get("description", "") + "\n" + data.get("text", "")).lower()
        for dest, keywords in keyword_map.items():
            if dest == src:
                continue
            matched = {kw for kw in keywords if kw and kw in text_blob}
            if matched:
                edges.setdefault((src, dest), set()).update(matched)

    mandatory_edges = [
        ("Conversation Engine", "Voice & Audio"),
        ("Voice & Audio", "Conversation Engine"),
        ("Conversation Engine", "Memory & Context"),
        ("Memory & Context", "Conversation Engine"),
        ("Evolution & Adaptation", "Conversation Engine"),
        ("Evolution & Adaptation", "Memory & Context"),
        ("Evolution & Adaptation", "Voice & Audio"),
        ("Conversation Engine", "Evolution & Adaptation"),
    ]
    for edge in mandatory_edges:
        edges.setdefault(edge, set())

    lines_out = [
        "digraph CleverCognitiveMap {",
        "  rankdir=LR;",
        '  graph [fontsize=14, fontname="Helvetica"];',
        '  node [shape="rectangle", style="filled,rounded", fontname="Helvetica", fontsize=12];',
        '  edge [fontname="Helvetica", fontsize=11];',
        "",
    ]

    for name in subsystems:
        color, label = node_styles.get(name, ("#ffffff", name))
        lines_out.append(f'  "{name}" [label="{label}", fillcolor="{color}"];')

    lines_out.append("")

    for (src, dest), keywords in sorted(edges.items()):
        if keywords:
            label = "/".join(sorted(keywords))
            lines_out.append(f'  "{src}" -> "{dest}" [label="{label}"];')
        else:
            lines_out.append(f'  "{src}" -> "{dest}";')

    lines_out.append("}")

    new_content = "\n".join(lines_out) + "\n"
    existing = ""
    if COGNITIVE_MAP_PATH.exists():
        existing = COGNITIVE_MAP_PATH.read_text(encoding="utf-8", errors="replace")

    if existing == new_content:
        return False

    COGNITIVE_MAP_PATH.write_text(new_content, encoding="utf-8")
    return True


def ensure_report_structure() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_history() -> List[Dict[str, object]]:
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_history(history: Sequence[Dict[str, object]]) -> None:
    HISTORY_PATH.write_text(json.dumps(list(history), indent=2), encoding="utf-8")


def update_history(manifest_stats: Dict[str, object]) -> List[Dict[str, object]]:
    ensure_report_structure()
    history = load_history()
    timestamp = str(manifest_stats.get("generated") or datetime.now().isoformat())
    record = {
        "timestamp": timestamp,
        "total_files": int(manifest_stats.get("total_files", 0)),
        "total_lines": int(manifest_stats.get("total_line_count", 0)),
        "file_types": manifest_stats.get("suffix_counts", {}),
    }

    if history and history[-1].get("timestamp") == record["timestamp"]:
        history[-1] = record
    else:
        history.append(record)

    save_history(history)
    return history


def generate_trend_charts(history: Sequence[Dict[str, object]]) -> List[Path]:
    ensure_report_structure()
    if not history or not _MATPLOTLIB_AVAILABLE:
        if not history:
            print("ℹ️  Not enough history to render charts yet.")
        elif not _MATPLOTLIB_AVAILABLE and _MATPLOTLIB_ERROR:
            print(f"⚠️  Matplotlib unavailable: {_MATPLOTLIB_ERROR}")
        return []

    dates: List[datetime] = []
    line_counts: List[int] = []

    for record in history:
        ts = record.get("timestamp")
        try:
            dt = datetime.fromisoformat(str(ts))
        except Exception:
            continue
        dates.append(dt)
        line_counts.append(int(record.get("total_lines", 0)))

    chart_paths: List[Path] = []
    if dates:
        plt.figure(figsize=(8, 4))
        plt.plot(dates, line_counts, marker="o")
        plt.title("Cumulative Line Count")
        plt.xlabel("Run")
        plt.ylabel("Total lines")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.gcf().autofmt_xdate()
        plt.savefig(LINE_CHART_PATH)
        plt.close()
        chart_paths.append(LINE_CHART_PATH)

    type_counter: Counter[str] = Counter()
    for record in history:
        for suffix, count in record.get("file_types", {}).items():
            type_counter[str(suffix)] = max(type_counter[str(suffix)], int(count))

    top_types = [suffix for suffix, _ in type_counter.most_common(5) if suffix]

    if top_types and dates:
        plt.figure(figsize=(8, 4))
        for suffix in top_types:
            series = [int(rec.get("file_types", {}).get(suffix, 0)) for rec in history]
            plt.plot(dates, series, marker="o", label=suffix or "no_ext")
        plt.title("File Type Counts (Top 5)")
        plt.xlabel("Run")
        plt.ylabel("Count")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.gcf().autofmt_xdate()
        plt.savefig(FILETYPE_CHART_PATH)
        plt.close()
        chart_paths.append(FILETYPE_CHART_PATH)

    return chart_paths


def build_report_entry(
    manifest_summary: str,
    manifest_stats: Dict[str, object],
    change_flags: Sequence[str],
    chart_paths: Sequence[Path],
    run_time: str,
    ipfs_cids: Optional[Dict[str, str]] = None,
    ipfs_message: Optional[str] = None,
) -> List[str]:
    lines: List[str] = []
    lines.append(f"## Run at {run_time}")
    lines.append("")
    lines.extend(
        [
            f"- Summary: {manifest_summary}",
            f"- Total files: {manifest_stats.get('total_files', 0)}",
            f"- Total lines: {manifest_stats.get('total_line_count', 0)}",
            f"- Updated artifacts: {', '.join(change_flags)}",
            "",
            "**Top File Types**",
        ]
    )

    top_suffixes = manifest_stats.get("top_suffixes", [])
    if top_suffixes:
        lines.append("")
        lines.append("| Type | Count |")
        lines.append("| --- | --- |")
        for suffix, count in top_suffixes:
            lines.append(f"| `{suffix}` | {count} |")
    else:
        lines.append("\n_No file type data available._")

    recent_files = manifest_stats.get("recent_files", [])
    lines.append("")
    lines.append("**Most Recent Files**")
    if recent_files:
        lines.append("")
        for item in recent_files:
            lines.append(f"- {item.get('path')} @ {item.get('modified')}")
    else:
        lines.append("\n_None recorded._")

    if chart_paths:
        lines.append("")
        lines.append("**Trend Charts**")
        lines.append("")
        for chart in chart_paths:
            lines.append(f"![{chart.name}]({chart.name})")
    elif not _MATPLOTLIB_AVAILABLE and _MATPLOTLIB_ERROR:
        lines.append("")
        lines.append(f"_Charts unavailable: {_MATPLOTLIB_ERROR}_")

    if ipfs_cids or ipfs_message:
        lines.append("")
        lines.append("**IPFS Snapshots**")
        lines.append("")
        if ipfs_cids:
            for artifact, cid in ipfs_cids.items():
                gateway = f"http://127.0.0.1:8081/ipfs/{cid}"
                lines.append(f"- {artifact}: [{cid}]({gateway})")
        if ipfs_message and not ipfs_cids:
            lines.append(f"_IPFS pinning skipped_: {ipfs_message}")

    lines.append("")
    return lines


def write_daily_report(
    manifest_summary: str,
    manifest_stats: Dict[str, object],
    change_flags: Sequence[str],
    chart_paths: Sequence[Path],
    run_time: str,
    ipfs_cids: Optional[Dict[str, str]] = None,
    rewrite_last: bool = False,
    ipfs_message: Optional[str] = None,
) -> Path:
    ensure_report_structure()
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORT_DIR / f"{date_str}.md"
    entry_lines = build_report_entry(
        manifest_summary,
        manifest_stats,
        change_flags,
        chart_paths,
        run_time,
        ipfs_cids=ipfs_cids,
        ipfs_message=ipfs_message,
    )
    entry_text = "\n".join(entry_lines)

    if not report_path.exists():
        header = [f"# Self-Reflection Summary — {date_str}", ""]
        report_path.write_text("\n".join(header) + entry_text, encoding="utf-8")
        return report_path

    if rewrite_last:
        current = report_path.read_text(encoding="utf-8")
        marker = f"## Run at {run_time}"
        start = current.rfind(marker)
        if start == -1:
            with report_path.open("a", encoding="utf-8") as handle:
                handle.write("\n---\n\n" + entry_text)
            return report_path
        delimiter = "\n---\n"
        prev = current.rfind(delimiter, 0, start)
        section_start = 0 if prev == -1 else prev + len(delimiter)
        next_idx = current.find(delimiter, start)
        section_end = len(current) if next_idx == -1 else next_idx
        new_text = current[:section_start] + entry_text + current[section_end:]
        report_path.write_text(new_text, encoding="utf-8")
        return report_path

    with report_path.open("a", encoding="utf-8") as handle:
        handle.write("\n---\n\n" + entry_text)

    return report_path


def record_self_reflection(
    manifest_summary: str,
    manifest_stats: Dict[str, object],
    change_flags: Sequence[str],
    report_path: Optional[Path],
    chart_paths: Sequence[Path],
) -> None:
    record_self_reflection_with_ipfs(
        manifest_summary,
        manifest_stats,
        change_flags,
        report_path,
        chart_paths,
        {},
    )


def record_self_reflection_with_ipfs(
    manifest_summary: str,
    manifest_stats: Dict[str, object],
    change_flags: Sequence[str],
    report_path: Optional[Path],
    chart_paths: Sequence[Path],
    ipfs_cids: Dict[str, str],
    ipfs_message: Optional[str] = None,
) -> None:
    timestamp = datetime.now().isoformat()
    cid_snippet = ""
    if ipfs_cids:
        cid_snippet = " | IPFS: " + ", ".join(f"{name}:{cid}" for name, cid in ipfs_cids.items())
    elif ipfs_message:
        cid_snippet = f" | IPFS status: {ipfs_message}"
    summary_with_ipfs = manifest_summary + cid_snippet

    if _EVOLUTION_AVAILABLE and get_evolution_engine is not None:
        try:
            evolution = get_evolution_engine()
            evolution.log_interaction(
                {
                    "interaction_type": "self_reflection",
                    "summary": summary_with_ipfs,
                    "artifacts": list(change_flags),
                    "manifest_total_files": manifest_stats.get("total_files"),
                    "manifest_total_lines": manifest_stats.get("total_line_count"),
                    "top_suffixes": manifest_stats.get("top_suffixes"),
                    "report_path": str(report_path) if report_path else None,
                    "chart_paths": [str(path) for path in chart_paths],
                    "ipfs_cids": ipfs_cids,
                    "timestamp": timestamp,
                }
            )
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"⚠️  Evolution engine logging failed: {exc}")
    elif _EVOLUTION_IMPORT_ERROR:
        print(f"⚠️  Evolution engine unavailable: {_EVOLUTION_IMPORT_ERROR}")

    if _MEMORY_AVAILABLE and get_memory_engine is not None and MemoryContext is not None:
        try:
            memory_engine = get_memory_engine()
            keywords = [
                "self_reflection",
                "manifest",
                "cognitive_map",
            ]
            for suffix, _count in manifest_stats.get("top_suffixes", [])[:3]:
                suffix_str = str(suffix)
                if suffix_str not in keywords:
                    keywords.append(suffix_str)

            recent_files = [
                item.get("path")
                for item in manifest_stats.get("recent_files", [])
                if isinstance(item, dict)
            ]

            context_links = [f"artifact:{flag}" for flag in change_flags]
            if report_path:
                context_links.append(f"report:{report_path.name}")
            context_links.extend(f"chart:{path.name}" for path in chart_paths)
            context_links.extend(f"ipfs:{cid}" for cid in ipfs_cids.values())
            if ipfs_message and not ipfs_cids:
                context_links.append(f"ipfs_status:{ipfs_message}")

            context = MemoryContext(
                user_input="Weekly self-reflection summary",
                timestamp=time.time(),
                session_id=f"self_reflection_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                mode="SystemUpdate",
                sentiment="neutral",
                keywords=keywords[:12],
                entities=[rf for rf in recent_files if rf][:12],
                response_text=summary_with_ipfs,
                importance_score=0.7,
                context_links=context_links or ["artifact:none"],
            )
            memory_engine.store_interaction(context)

            if ipfs_cids:
                ipfs_context = MemoryContext(
                    user_input="Pinned self-reflection artifacts to IPFS",
                    timestamp=time.time(),
                    session_id=f"ipfs_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    mode="ipfs_snapshot",
                    sentiment="positive",
                    keywords=["ipfs_snapshot", *list(ipfs_cids.values())],
                    entities=list(ipfs_cids.keys())[:12],
                    response_text="IPFS snapshot CIDs: "
                    + ", ".join(f"{name}:{cid}" for name, cid in ipfs_cids.items()),
                    importance_score=0.6,
                    context_links=[f"ipfs:{cid}" for cid in ipfs_cids.values()],
                )
                memory_engine.store_interaction(ipfs_context)
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"⚠️  Memory engine storage failed: {exc}")
    elif _MEMORY_IMPORT_ERROR:
        print(f"⚠️  Memory engine unavailable: {_MEMORY_IMPORT_ERROR}")


def maybe_push_changes(committed: bool) -> None:
    """Optionally push the commit upstream when configured."""
    if not committed:
        return
    push_flag = os.environ.get("SELF_REFLECTION_AUTO_PUSH", "")
    if push_flag.lower() not in {"1", "true", "yes"}:
        return
    try:
        subprocess.run(["git", "push"], cwd=REPO_ROOT, check=True)
        print("📤 Pushed self-reflection update to remote.")
    except subprocess.CalledProcessError as exc:  # pragma: no cover - best effort
        print(f"⚠️  Git push failed: {exc}")


def maybe_pin_to_ipfs(paths: Sequence[Path]) -> Tuple[Dict[str, str], Optional[str]]:
    """Pin artifacts to IPFS when enabled; return mapping of filename->CID and an optional warning."""
    results: Dict[str, str] = {}
    warning: Optional[str] = None
    flag = os.environ.get("SELF_REFLECTION_IPFS_PUSH", "")
    if flag.lower() not in {"1", "true", "yes"}:
        return results, warning

    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        try:
            cid = (
                subprocess.check_output(
                    ["ipfs", "add", "-Q", str(path)],
                    cwd=REPO_ROOT,
                )
                .decode("utf-8")
                .strip()
            )
            results[path.name] = cid
        except FileNotFoundError:
            warning = "IPFS command not found"
            print("⚠️  IPFS command not found; skipping IPFS pinning.")
            return {}, warning
        except subprocess.CalledProcessError as exc:
            msg = f"{path.name}: {exc}"
            warning = msg if warning is None else f"{warning}; {msg}"
            print(f"⚠️  IPFS pin failed for {path.name}: {exc}")
            continue
    return results, warning


def write_last_ipfs_cids(ipfs_cids: Dict[str, str]) -> None:
    if not ipfs_cids:
        return
    ensure_report_structure()
    LAST_IPFS_PATH.write_text(json.dumps(ipfs_cids, indent=2), encoding="utf-8")


def commit_changes() -> bool:
    """Stage and commit artifacts; return True if commit created."""
    base_paths = [MANIFEST_PATH, COGNITIVE_MAP_PATH]
    base_existing = [str(path) for path in base_paths if Path(path).exists()]
    if base_existing:
        subprocess.run(
            ["git", "add", *base_existing],
            cwd=REPO_ROOT,
            check=True,
        )

    forced_paths = []
    if REPORT_DIR.exists():
        forced_paths.append(str(REPORT_DIR))
    if HISTORY_PATH.exists():
        forced_paths.append(str(HISTORY_PATH))

    if forced_paths:
        subprocess.run(
            ["git", "add", "-f", *forced_paths],
            cwd=REPO_ROOT,
            check=True,
        )
    diff_result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=REPO_ROOT,
    )
    if diff_result.returncode == 0:
        return False

    subprocess.run(
        ["git", "commit", "-m", "🧠 Self-reflection update"],
        cwd=REPO_ROOT,
        check=True,
    )
    return True


def main() -> None:
    os.chdir(REPO_ROOT)
    manifest_changed, manifest_summary, manifest_stats = generate_manifest()
    map_changed = generate_cognitive_map()
    run_time = datetime.now().strftime("%H:%M:%S")

    change_flags: List[str] = []
    if manifest_changed:
        change_flags.append("manifest")
    if map_changed:
        change_flags.append("cognitive_map")
    if not change_flags:
        change_flags.append("report_only")

    history = update_history(manifest_stats)
    chart_paths = generate_trend_charts(history)
    ipfs_cids: Dict[str, str] = {}
    ipfs_messages: List[str] = []
    artifact_candidates: List[Path] = [MANIFEST_PATH, COGNITIVE_MAP_PATH]
    artifact_candidates.extend([path for path in chart_paths if Path(path).exists()])
    initial_ipfs, initial_warning = maybe_pin_to_ipfs(artifact_candidates)
    if initial_ipfs:
        ipfs_cids.update(initial_ipfs)
    if initial_warning:
        ipfs_messages.append(initial_warning)

    report_path = write_daily_report(
        manifest_summary=manifest_summary,
        manifest_stats=manifest_stats,
        change_flags=change_flags,
        chart_paths=chart_paths,
        run_time=run_time,
        ipfs_cids=ipfs_cids if ipfs_cids else None,
        ipfs_message="; ".join(ipfs_messages) if ipfs_messages else None,
    )

    report_ipfs, report_warning = maybe_pin_to_ipfs([report_path])
    if report_ipfs:
        ipfs_cids.update(report_ipfs)
        report_path = write_daily_report(
            manifest_summary=manifest_summary,
            manifest_stats=manifest_stats,
            change_flags=change_flags,
            chart_paths=chart_paths,
            run_time=run_time,
            ipfs_cids=ipfs_cids,
            rewrite_last=True,
            ipfs_message="; ".join(ipfs_messages) if ipfs_messages else None,
        )
    if report_warning:
        ipfs_messages.append(report_warning)

    if ipfs_messages and not ipfs_cids:
        report_path = write_daily_report(
            manifest_summary=manifest_summary,
            manifest_stats=manifest_stats,
            change_flags=change_flags,
            chart_paths=chart_paths,
            run_time=run_time,
            ipfs_cids=None,
            rewrite_last=True,
            ipfs_message="; ".join(ipfs_messages),
        )

    write_last_ipfs_cids(ipfs_cids)

    committed = commit_changes()
    if committed:
        if ipfs_cids:
            print("📦 IPFS snapshots pinned:")
            for name, cid in ipfs_cids.items():
                print(f"  - {name}: {cid}")
        print("Committed refreshed manifest, cognitive map, and self-reflection report.")
        maybe_push_changes(committed=True)
    else:
        print("No git changes detected; nothing committed.")

    record_self_reflection_with_ipfs(
        manifest_summary=manifest_summary,
        manifest_stats=manifest_stats,
        change_flags=change_flags,
        report_path=report_path,
        chart_paths=chart_paths,
        ipfs_cids=ipfs_cids,
        ipfs_message="; ".join(ipfs_messages) if ipfs_messages else None,
    )


if __name__ == "__main__":
    main()
