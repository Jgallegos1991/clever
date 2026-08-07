#!/bin/bash
# Disable Pylance and restart VS Code with memory optimization

echo "🧠 Clever Memory Optimization - Disabling Pylance"
echo "=================================================="

# Disable Pylance extension
echo "Disabling Pylance extension..."
code --disable-extension ms-python.vscode-pylance

# Kill any existing VS Code processes to ensure clean restart
echo "Stopping VS Code processes..."
pkill -f "code"
sleep 2

# Start VS Code with memory optimization flags
echo "Starting VS Code with memory optimization..."
code --max-memory=2048 --disable-gpu --disable-dev-shm-usage /home/jgallegos1991/Clever

echo "✅ VS Code restarted with Pylance disabled and memory optimized"
echo "Memory usage should be significantly reduced now"
echo ""
echo "Alternative: You can use lightweight alternatives:"
echo "- Basic Python syntax highlighting (built-in)"
echo "- Manual code analysis with make lint"
echo "- Custom static analysis tools in the project"