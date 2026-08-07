#!/usr/bin/env python3
"""
start_clever_complete.py - Complete Remote Access Setup for Clever

Why: Provides both Clever UI access AND VS Code Server for remote file editing
     enabling full cognitive partnership and development workflow from any device
     on Jay's Tailscale network.

Where: Standalone startup script that launches both Clever Flask app and VS Code Server
       for complete remote development and interaction experience.

How: Starts Clever on port 5000 and VS Code Server on port 8080, both accessible
     via Tailscale network for secure remote access to digital brain extension.

File Usage:
    - Primary purpose: Complete remote access to Clever ecosystem
    - Clever UI: Port 5000 for cognitive partnership interaction
    - VS Code Server: Port 8080 for remote file editing and development
    - Tailscale integration: Secure remote access from any authorized device

Connects to:
    - tailscale_config.py: Network configuration and IP detection
    - app.py: Clever Flask application startup
    - code-server: VS Code Server for remote file editing
"""

import subprocess
import sys
import threading
import time
from pathlib import Path

# Add Clever directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tailscale_config import configure_flask_for_tailscale, get_tailscale_ip, get_tailscale_status


def start_code_server(tailscale_ip):
    """
    Start VS Code Server on port 8080 for remote file editing.

    Why: Enables remote development and file editing capabilities
    Where: Runs as background process alongside Clever Flask app
    How: Launches code-server bound to all interfaces on port 8080
    """
    print("🔧 Starting VS Code Server for remote file editing...")

    try:
        # Configure code-server to bind to all interfaces
        cmd = [
            "code-server",
            "--bind-addr",
            "0.0.0.0:8080",
            "--auth",
            "none",  # No auth needed since Tailscale provides security
            "--disable-telemetry",
            "--disable-update-check",
            "/home/jgallegos1991/Clever",  # Open Clever directory
        ]

        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"✅ VS Code Server: http://{tailscale_ip}:8080")
        print("📝 Ready for remote file editing!")

    except Exception as e:
        print(f"❌ Failed to start VS Code Server: {e}")


def start_clever_app():
    """
    Start Clever Flask application.

    Why: Provides Clever's digital brain extension interface
    Where: Runs as main process for cognitive partnership interaction
    How: Imports and starts Flask app with Tailscale configuration
    """
    try:
        from app import app

        # Configure for remote access
        flask_config = configure_flask_for_tailscale()
        if not flask_config["success"]:
            print(f"❌ Flask configuration error: {flask_config.get('error')}")
            return False

        # Start Flask with Tailscale configuration
        app.run(
            host="0.0.0.0",  # Accept connections from all Tailscale devices
            port=5000,
            debug=False,  # Security: disable debug for remote access
            threaded=True,  # Handle multiple remote connections
        )

    except Exception as e:
        print(f"❌ Error starting Clever: {e}")
        return False


def main():
    """Main startup function for complete Clever remote access."""

    print("🧠 Starting Complete Clever Remote Access Setup")
    print("🌐 Configuring Tailscale Network Access")
    print("=" * 70)

    # Check Tailscale connectivity
    tailscale_ip = get_tailscale_ip()
    if not tailscale_ip:
        print("❌ Tailscale not connected!")
        print("Run: sudo tailscale up")
        return False

    print(f"✅ Tailscale IP: {tailscale_ip}")

    # Get network status
    status = get_tailscale_status()
    print(f"📱 Connected Devices: {len(status.get('devices', []))}")

    for device in status.get("devices", []):
        status_icon = "🟢" if device["status"] != "offline" else "🔴"
        print(f"   {status_icon} {device['hostname']} ({device['os']})")

    print()
    print("🚀 Starting Complete Clever Ecosystem...")
    print()
    print("📋 Remote Access URLs:")
    print(f"🧠 Clever UI:        http://{tailscale_ip}:5000")
    print(f"📝 VS Code Server:   http://{tailscale_ip}:8080")
    print()
    print("💡 Usage:")
    print("   • Port 5000: Chat with Clever, cognitive partnership")
    print("   • Port 8080: Edit Clever's files, development work")
    print()
    print("📱 Bookmark both URLs on your remote devices!")
    print("Press Ctrl+C to stop all services")
    print("=" * 70)

    # Start VS Code Server in background
    code_server_thread = threading.Thread(target=start_code_server, args=(tailscale_ip,))
    code_server_thread.daemon = True
    code_server_thread.start()

    # Give code-server time to start
    time.sleep(3)

    # Start Clever Flask app (blocking)
    try:
        start_clever_app()
    except KeyboardInterrupt:
        print("\n👋 Shutting down Clever ecosystem gracefully...")
        print("   🧠 Clever UI stopped")
        print("   📝 VS Code Server stopped")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
