# 📱 Mobile Access to Clever via Termius

## 🌐 Direct Browser Access (Recommended)
**Just open your phone's browser and go to:**
- 🧠 **Clever UI**: `http://100.124.203.114:5000`
- 📝 **VS Code Server**: `http://100.124.203.114:8080`

## 🔧 Termius SSH Setup

### SSH Connection Details:
```
Host: 100.124.203.114
Username: jgallegos1991
Port: 22
```

### Port Forwarding Setup in Termius:
1. **Clever UI Forwarding:**
   - Local: 5000
   - Remote: localhost:5000

2. **VS Code Server Forwarding:**
   - Local: 8080  
   - Remote: localhost:8080

### After SSH Connection:
- Open browser on phone
- Go to `localhost:5000` for Clever
- Go to `localhost:8080` for VS Code

## 📋 Quick Commands for Termius Terminal

```bash
# Check if services are running
ps aux | grep -E "(flask|code-server)"

# Check Tailscale status
tailscale status

# Restart Clever if needed
cd /home/jgallegos1991/Clever && make run

# Restart VS Code Server if needed
code-server --bind-addr 0.0.0.0:8080 --auth none /home/jgallegos1991/Clever
```

## 🔍 Troubleshooting

### If you can't connect:
1. **Check Tailscale on phone**: Make sure phone is connected to Tailscale
2. **Check services**: SSH in and run `ps aux | grep flask`
3. **Restart services**: Use the commands above

### Alternative URLs (if main doesn't work):
- Try `http://localhost:5000` and `http://localhost:8080` after SSH port forwarding
- Or use the full Tailscale IP: `100.124.203.114`

## 💡 Pro Tips

1. **Bookmark URLs** in your phone browser for quick access
2. **Use Termius favorites** to save the SSH connection
3. **Enable auto-connect** in Termius for seamless access
4. **Use split-screen** on Android to have both Clever UI and code editing open

## 🚀 Mobile Development Workflow

1. **SSH into system** via Termius
2. **Open Clever UI** in browser tab 1 (port 5000)
3. **Open VS Code** in browser tab 2 (port 8080)  
4. **Code and chat** seamlessly between both interfaces
5. **Use terminal** in Termius for git operations and system commands

**You now have full mobile development access to Clever!** 🧠📱✨