#!/bin/bash
"""
start_services.sh - Auto-start script for Clever remote services

Why: Ensures both Clever UI and VS Code Server are running for remote access
Where: Can be run manually or set up as systemd service for auto-start
How: Starts both Flask app and code-server in background with proper logging
"""

echo "🚀 Starting Clever Remote Services..."

# Function to check if service is running
check_service() {
    local port=$1
    local name=$2
    if netstat -tulpn 2>/dev/null | grep ":$port" > /dev/null; then
        echo "✅ $name is running on port $port"
        return 0
    else
        echo "❌ $name is NOT running on port $port"
        return 1
    fi
}

# Check Tailscale
TAILSCALE_IP=$(tailscale ip | head -n1 | grep '\.')
if [ -z "$TAILSCALE_IP" ]; then
    echo "❌ Tailscale not connected! Run: sudo tailscale up"
    exit 1
fi
echo "✅ Tailscale IP: $TAILSCALE_IP"

# Start Clever if not running
if ! check_service 5000 "Clever UI"; then
    echo "🧠 Starting Clever UI..."
    cd /home/jgallegos1991/Clever
    nohup make run > /tmp/clever.log 2>&1 &
    sleep 5
    check_service 5000 "Clever UI"
fi

# Start VS Code Server if not running  
if ! check_service 8080 "VS Code Server"; then
    echo "📝 Starting VS Code Server..."
    nohup code-server --bind-addr 0.0.0.0:8080 --auth none --disable-telemetry --disable-update-check /home/jgallegos1991/Clever > /tmp/code-server.log 2>&1 &
    sleep 3
    check_service 8080 "VS Code Server"
fi

echo ""
echo "📋 Remote Access URLs:"
echo "🧠 Clever UI:        http://$TAILSCALE_IP:5000"
echo "📝 VS Code Server:   http://$TAILSCALE_IP:8080"
echo ""
echo "📱 These URLs work from any device on your Tailscale network!"
echo "🔍 Logs: /tmp/clever.log and /tmp/code-server.log"