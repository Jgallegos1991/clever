#!/usr/bin/env python3
"""
Continuous hardware memory observer for Clever runtime.

Why: Keep Clever within the 3.7 GB RAM constraint so persona, NLP, and evolution
engines never degrade due to host resource starvation.
Where: Called by `make memory-monitor` and other maintenance scripts when Jay
needs a live, offline-safe read on system memory.
How: Streams `/proc/meminfo`, parses the values we care about, and prints a
compact summary that downstream monitors can scrape.

File Usage:
    - `make memory-monitor`: launches continuous monitoring loop for diagnostics.
    - `memory_monitor.py`: imports `check_memory()` for reusable health probes.
Connects to:
    - `hardware_optimizer.py`: uses the same MemAvailable metrics for tuning.
    - `logs/codex_diagnostics/`: stores captured outputs during routine audits.
"""


def check_memory():
    """
    Check and report the current memory status from `/proc/meminfo`.

    Why: Provide near-real-time visibility into available memory so Codex can
    react before Clever exceeds device limits.
    Where: Invoked inside this module’s CLI loop and by system diagnostics that
    import the helper.
    How: Reads kernel memory counters, normalizes units, and returns structured
    values for human-readable output.

    File Usage:
        - `monitor_memory.py`: emits per-interval stats in the CLI loop.
        - `hardware_optimizer.py`: can reuse the values for adaptive strategies.
    Connects to:
        - `/proc/meminfo`: authoritative memory source on Linux.
        - `logs/codex_diagnostics/`: downstream tools log formatted readings.
    """
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()

        memory = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                value = "".join(filter(str.isdigit, value))
                if value:
                    memory[key.strip()] = int(value) * 1024

        available_mb = memory.get("MemAvailable", 0) / (1024 * 1024)
        total_mb = memory.get("MemTotal", 0) / (1024 * 1024)

        return available_mb, total_mb

    except Exception as e:
        print(f"Memory check failed: {e}")
        return 800, 2700


def monitor_clever_memory():
    """
    Monitor Clever's memory usage continuously.

    Why: Provide a persistent watch that flags low-memory conditions before they
    impact persona or NLP performance.
    Where: Invoked when this module runs as a script or by automation routines
    that need ongoing visibility.
    How: Calls `check_memory()` each minute, logs stats, and triggers emergency
    optimization when resources dip below 10 percent.

    File Usage:
        - `monitor_memory.py`: primary entry point for live monitoring.
    Connects to:
        - `revolutionary_memory_strategy.py`: invoked for emergency mitigation.
        - `logs/codex_diagnostics/`: downstream processes record the output.
    """
    print("🔄 Starting Clever memory monitoring...")

    try:
        while True:
            available, total = check_memory()
            usage_percent = ((total - available) / total) * 100

            print(f"Memory: {available:.0f}MB available ({usage_percent:.1f}% used)")

            # Alert if memory gets critically low
            if available < total * 0.1:  # Less than 10% available
                print("🚨 CRITICAL: Memory pressure detected!")
                subprocess.run(["python3", "revolutionary_memory_strategy.py"], capture_output=True)

            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        print("\n👋 Memory monitoring stopped")


if __name__ == "__main__":
    monitor_clever_memory()
