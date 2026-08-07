# hub/bin/start.sh
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
LOG="$ROOT/logs/hub.log"
STATE="$ROOT/data/state"
mkdir -p "$STATE"

# tiny python supervisor in-line (no new deps)
python3 - "$ROOT" >> "$LOG" 2>&1 <<'PY'
import os, sys, time, json, subprocess, signal
from pathlib import Path
ROOT = Path(sys.argv[1])
CFG = ROOT/"config/hub.yaml"

def yload(p):
    import yaml  # spacy already brought PyYAML in many stacks; if not, quick fallback:
    return yaml.safe_load(p.read_text())
try:
    import yaml
except Exception:
    print("[warn] PyYAML missing; using minimal parser.")
    def _min(s):
        # very basic: accept only our current YAML (colon map + arrays)
        import re, ast
        s = re.sub(r'#.*','',s)
        s = s.replace(': true', ': True').replace(': false', ': False').replace('null','None')
        return ast.literal_eval('{'+s.split('{',1)[1].rsplit('}',1)[0]+'}')
    def yload(p): return _min(p.read_text())

cfg = yload(CFG)
procs = {}

def spawn(svc):
    name = svc["name"]
    cwd = ROOT / svc["cwd"]
    cmd = svc["cmd"]
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"]="1"
    print(f"[hub] starting {name}: {cmd} (cwd={cwd})")
    p = subprocess.Popen(cmd, cwd=str(cwd), env=env)
    procs[name] = {"p": p, "cfg": svc, "fail": 0, "last": time.time()}

def is_healthy_http(url, timeout):
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return 200 <= r.status < 300
    except Exception:
        return False

def is_healthy_proc(substr):
    try:
        out = subprocess.check_output(["ps","aux"], text=True)
        return substr in out
    except Exception:
        return False

# spawn all
for svc in cfg["services"]:
    spawn(svc)

try:
    while True:
        for name, meta in list(procs.items()):
            p = meta["p"]; svc = meta["cfg"]
            dead = (p.poll() is not None)
            ok = False
            health = svc.get("health", {})
            if not dead:
                if health.get("type") == "http":
                    ok = is_healthy_http(health["url"], health.get("timeout_sec",2))
                elif health.get("type") == "process":
                    ok = is_healthy_proc(health.get("probe",""))
                else:
                    ok = True
            if dead or not ok:
                print(f"[hub] {name} unhealthy (dead={dead}, ok={ok}).")
                if svc.get("restart") == "on-failure":
                    backoff = svc.get("backoff",[2,5,10])
                    i = meta["fail"]; delay = backoff[min(i, len(backoff)-1)]
                    meta["fail"] = i+1
                    print(f"[hub] restarting {name} in {delay}s …")
                    time.sleep(delay)
                    try: spawn(svc)
                    except Exception as e: print(f"[hub] spawn error {name}: {e}")
                else:
                    print(f"[hub] not restarting {name}")
            time.sleep(1)
        time.sleep(2)
except KeyboardInterrupt:
    pass
finally:
    for name, meta in procs.items():
        try:
            meta["p"].terminate()
        except Exception:
            pass
    time.sleep(1)
PY

# autostart via cron (idempotent)
if grep -q "@reboot .*Synaptic-Hub/hub/bin/start.sh" <(crontab -l 2>/dev/null); then
  :
else
  (crontab -l 2>/dev/null; echo "@reboot bash $ROOT/hub/bin/start.sh") | crontab -
fi
echo "[hub] supervisor started; logs at $LOG"
