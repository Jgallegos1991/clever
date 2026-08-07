#!/bin/bash
# Quick Clever Status Check Script

echo "🧠 CLEVER AI STATUS CHECK"
echo "========================"

# Check if Clever is running
if pgrep -f "python.*app.py" > /dev/null; then
    echo "✅ Clever is RUNNING!"
    echo "   Process ID: $(pgrep -f 'python.*app.py')"
    echo "   Access URL: http://localhost:5000"
    if command -v tailscale > /dev/null && tailscale status > /dev/null 2>&1; then
        echo "   Tailscale: http://penguin:5000"
    fi
else
    echo "❌ Clever is NOT running"
    echo "   Run: ./start_clever.sh to start her up!"
fi

# Show system resources
echo ""
echo "📊 System Resources:"
echo "   Memory Available: $(free -h | awk 'NR==2{printf "%.1fGB", $7/1024/1024}')"
echo "   CPU Load: $(uptime | awk -F'load average:' '{ print $2 }' | awk '{ print $1 }' | sed 's/,//')"

# Check VS Code status
if pgrep -f "code" > /dev/null; then
    vs_code_memory=$(ps aux | grep -v grep | grep code | awk '{sum += $6} END {printf "%.1fMB", sum/1024}')
    echo "   VS Code: RUNNING (using $vs_code_memory)"
else
    echo "   VS Code: Not running"
fi

echo ""