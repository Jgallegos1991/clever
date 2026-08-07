# Makefile — Clever (offline-first, Jay-only)
# Usage:
#   make setup          # create venv + install deps (base + full if present)
#   make run            # start Flask on http://localhost:5000
#   make fmt            # format python with black
#   make lint           # lint python with flake8
#   make test           # run pytest if tests/ exists
#   make ingest         # trigger a local ingestion POST
#   make freeze         # write requirements-lock.txt
#   make clean-venv     # remove .venv

.PHONY: default venv install setup setup-full setup-min setup-ipfs setup-sync-root run fmt lint test ingest ingest-pdfs freeze clean-venv watch watch-pdfs sync-and-ingest tailscale-setup tailscale-status help docstrings memory-status memory-optimize memory-monitor memory-emergency memory-strategies hardware-optimize setup-voice voice test-voice install-hooks enable-hooks disable-hooks

PY ?= python3
VENV ?= .venv
PIP  = $(PY) -m pip
ACTIVATE = . $(VENV)/bin/activate

FLASK_APP ?= app.py
FLASK_ENV ?= development
HOST ?= 0.0.0.0
PORT ?= 5000

default: run

venv:
	$(PY) -m venv $(VENV)

install: venv
	$(ACTIVATE) && $(PIP) install -U pip wheel
	@test -f requirements-base.txt && ( $(ACTIVATE) && $(PIP) install -r requirements-base.txt ) || true
	@test -f requirements.txt      && ( $(ACTIVATE) && $(PIP) install -r requirements.txt )      || true

# Developer convenience: install local git hooks
install-hooks:
	@echo "🔒 Installing local git hooks (.githooks)"
	@chmod +x .githooks/* 2>/dev/null || true
	@git config core.hooksPath .githooks
	@echo "✅ Hooks active. Local pre-push protection enabled."

# Explicit enable/disable toggles for hooks
enable-hooks: install-hooks
	@true

disable-hooks:
	@echo "⚠️  Disabling local git hooks for this repo"
	@git config --unset core.hooksPath || true
	@echo "✅ Hooks disabled. Remember: you lose local push protections."

# Minimal setup for offline-only operation (Flask only)
setup-min: venv setup-ipfs
	$(ACTIVATE) && $(PIP) install -U pip wheel
	$(ACTIVATE) && $(PIP) install -r requirements-min.txt
	@echo "✅ Minimal env ready. Only Flask installed for offline-only testing."

# Base setup with core dependencies (offline capable)
setup: install setup-ipfs hardware-optimize
	@echo "✅ Env ready. DB will initialize on first app start at $$PWD/clever.db (offline runtime)."

# Legacy sync root symlink for tooling compatibility
setup-sync-root:
	@echo "🔗 Ensuring legacy sync link exists at $$HOME/Clever_Sync..."
	@if [ ! -L "$$HOME/Clever_Sync" ]; then \
		ln -sfn "$$PWD/data/sync/clever_sync" "$$HOME/Clever_Sync"; \
		echo "✅ Linked $$HOME/Clever_Sync -> $$PWD/data/sync/clever_sync"; \
	else \
		echo "✅ Legacy sync link already exists."; \
	fi

# Full setup with all dependencies including NLP models (requires internet)
setup-full: install setup-ipfs
	@test -f requirements.txt && ( $(ACTIVATE) && $(PIP) install -r requirements.txt ) || true
	@echo "📥 Downloading spaCy model (requires internet)..."
	@$(ACTIVATE) && python -m spacy download en_core_web_sm || echo "⚠️  spaCy model download failed - offline NLP may be limited"
	$(MAKE) hardware-optimize
	@echo "✅ Full env ready with NLP capabilities and hardware optimization."

# IPFS repository setup (canonical brain store)
setup-ipfs:
	@echo "🧩 Ensuring canonical IPFS repo exists at $$PWD/ipfs_repo..."
	@mkdir -p ipfs_repo
	@if command -v ipfs >/dev/null 2>&1; then \
		if [ ! -f "$$PWD/ipfs_repo/config" ]; then \
			echo "📦 Initializing IPFS repo (IPFS_PATH=$$PWD/ipfs_repo)..."; \
			IPFS_PATH="$$PWD/ipfs_repo" ipfs init; \
		else \
			echo "✅ IPFS repo already initialized."; \
		fi; \
	else \
		echo "⚠️  ipfs command not found; repo directory created but not initialized."; \
		echo "   Install IPFS (kubo) and run: IPFS_PATH=$$PWD/ipfs_repo ipfs init"; \
	fi

# Voice System Setup (Chrome OS optimized with enhanced quality)
setup-voice: setup
	@echo "🎤 Setting up Clever's enhanced voice system for Chrome OS..."
	@$(ACTIVATE) && python setup_voice_system.py
	@echo "✨ Enhanced voice system configured with better TTS quality!"

# Start Clever's enhanced voice interaction
voice: setup-voice
	@echo "🧠 Starting Clever's enhanced voice system..."
	@echo "💡 Say 'Hey Clever' to activate voice interaction"
	@echo "🎭 Now with improved voice quality and personalities!"
	@$(ACTIVATE) && python clever_voice_loop.py

# Test enhanced voice system functionality
test-voice: setup-voice
	@echo "🧪 Testing enhanced voice system functionality..."
	@$(ACTIVATE) && python -c "from enhanced_voice_engine import EnhancedVoiceEngine; ve = EnhancedVoiceEngine(); print('✅ Enhanced voice engine ready')"
	@echo "🎭 Testing voice personalities..."
	@$(ACTIVATE) && timeout 15 python enhanced_voice_engine.py || echo "✅ Voice personality test completed"

# Hardware-aware optimization
hardware-optimize:
	@echo "🧠 Applying hardware optimization for 3.7GB RAM constraint..."
	@$(ACTIVATE) && python startup_optimizer.py || echo "⚠️  Hardware optimization completed with warnings"

# Memory Management for 3.7GB RAM Constraint
memory-status:
	@echo "🧠 Checking hardware profile and memory status..."
	@$(ACTIVATE) && python3 hardware_optimizer.py --profile

memory-optimize:
	@echo "⚡ Applying hardware-aware optimization..."
	@$(ACTIVATE) && python3 hardware_optimizer.py

memory-monitor:
	@echo "🔍 Starting continuous hardware monitoring..."
	@echo "Press Ctrl+C to stop monitoring"
	@$(ACTIVATE) && python3 hardware_optimizer.py --monitor

memory-emergency:
	@echo "🚨 EMERGENCY: Forcing aggressive memory optimization..."
	@$(ACTIVATE) && python3 startup_optimizer.py

memory-strategies:
	@echo "📋 Available optimization strategies:"
	@$(ACTIVATE) && python3 hardware_optimizer.py --strategies

run: hardware-optimize
	@echo "🚀 Starting Clever with optimized hardware configuration..."
	$(ACTIVATE) && FLASK_APP=$(FLASK_APP) FLASK_ENV=$(FLASK_ENV) flask run --host=$(HOST) --port=$(PORT)

fmt:
	$(ACTIVATE) && black .

lint:
	$(ACTIVATE) && flake8 .

test:
	# Run diagnostics drift check before executing full test suite
	# Non-canonical diagnostics now live under legacy/
	$(ACTIVATE) && $(PY) legacy/diagnostics_check.py
	$(ACTIVATE) && pytest

# Offline compliance testing
test-offline:
	@echo "🔍 Testing offline compliance..."
	@chmod +x test-offline.sh
	@./test-offline.sh

# System diagnostics
diagnostics:
	@echo "🔧 Running system diagnostics..."
	# Non-canonical diagnostics now live under legacy/
	$(ACTIVATE) && $(PY) legacy/diagnostics_check.py

# Enforce Why/Where/How docstring presence across codebase
docstrings:
	$(ACTIVATE) && $(PY) tools/docstring_enforcer.py --fail-on-missing --min-coverage 0.90 || (echo "❌ Docstring enforcement failed" && exit 1)

# Auto-generate file inventory
file-inventory:
	$(ACTIVATE) && python tools/generate_file_inventory.py
	@test -d tests && ( $(ACTIVATE) && pytest -q ) || echo "No tests/ directory; skipping."

ingest:
	@echo "POST /ingest"
	@curl -s -X POST http://127.0.0.1:$(PORT)/ingest \
		-H "Content-Type: application/json" \
		-d '{"action":"scan"}' || true

# Enhanced PDF ingestion
ingest-pdfs:
	@echo "📚 Processing PDFs and documents..."
	$(ACTIVATE) && python pdf_ingestor.py

# Ingest knowledge from Clever_Learn directory
ingest-knowledge:
	@echo "🧠 Ingesting knowledge files from Clever_Learn..."
	$(ACTIVATE) && python ingest_knowledge.py --verbose

# Watch sync directories for changes and auto-ingest  
watch:
	@echo "👀 Starting sync directory watcher..."
	$(ACTIVATE) && python sync_watcher.py

# Enhanced file watcher with PDF support
watch-pdfs:
	@echo "👁️  Starting enhanced file watcher with PDF support..."
	$(ACTIVATE) && python pdf_ingestor.py watch

# Best-effort rclone syncs then ingest both roots
sync-and-ingest:
	@echo "🔄 Running sync tools and ingesting content..."
	$(ACTIVATE) && python sync_tools.py || echo "⚠️  sync_tools.py not found or failed"

freeze:
	$(ACTIVATE) && $(PIP) freeze > requirements-lock.txt && echo "📦 Wrote requirements-lock.txt"

clean-venv:
	rm -rf $(VENV)

# Evolution Commands
evolution-status:
	@echo "🧠 Checking Clever's Evolution Status..."
	@$(ACTIVATE) && $(PY) -c "from evolution_engine import get_evolution_engine; import json; engine = get_evolution_engine(); status = engine.get_evolution_status(); print(f'🌟 Evolution Score: {status[\"evolution_score\"]:.1%}'); print(f'🔗 Concepts: {status[\"concept_count\"]}'); print(f'⚡ Connections: {status[\"connection_count\"]}'); print(f'📊 Network Density: {status[\"network_density\"]:.1%}'); print('🚀 Top Capabilities:'); [print(f'  {cap.replace(\"_\", \" \").title()}: {level:.1%}') for cap, level in sorted(status.get('capabilities', {}).items(), key=lambda x: x[1], reverse=True)[:5]]; print('📈 Recent Evolution Events:'); [print(f'  {event[1]}') for event in status.get('recent_events', [])[:3]]"

trigger-evolution:
	@echo "✨ Triggering Evolution Cascade..."
	@$(ACTIVATE) && $(PY) -c "from evolution_engine import get_evolution_engine; engine = get_evolution_engine(); clusters = engine.trigger_evolution_cascade(); print(f'🌟 Evolution cascade completed!'); print(f'🔮 Discovered {len(clusters)} knowledge clusters'); [print(f'  Cluster {i+1}: {cluster[\"size\"]} concepts') for i, cluster in enumerate(clusters[:3])]"

evolution-learn:
	@echo "📚 Triggering Learning from Sync Folder..."
	@$(ACTIVATE) && $(PY) -c "from file_ingestor import FileIngestor; from evolution_engine import get_evolution_engine; print('🔍 Scanning for new knowledge...'); ingestor = FileIngestor('./Clever_Sync'); ingestor.ingest_all_files(); print('🧠 Processing evolution learning...'); engine = get_evolution_engine(); status = engine.get_evolution_status(); print(f'✨ Learning complete! Evolution: {status[\"evolution_score\"]:.1%}')"

help:
	@echo "Clever AI Development Commands:"
	@echo ""
	@echo "🏗️  Setup Commands:"
	@echo "  setup-min        Install minimal dependencies (Flask only, offline)"
	@echo "  setup            Install base dependencies (offline capable)"
	@echo "  setup-full       Install all dependencies + NLP models (requires internet)"
	@echo "  setup-voice      Configure enhanced voice system for Chrome OS device"
	@echo ""
	@echo "🚀 Core Commands:"
	@echo "  run              Start Flask development server"
	@echo "  voice            Start Clever's enhanced voice interaction system"
	@echo "  test             Run pytest test suite"
	@echo "  test-voice       Test enhanced voice system and personalities"
	@echo "  fmt              Format code with black"
	@echo "  lint             Lint code with flake8"
	@echo ""
	@echo "📚 Content Processing:"
	@echo "  ingest           Trigger manual ingestion via API"
	@echo "  ingest-pdfs      Process PDFs and documents in Clever_Learn/"
	@echo "  watch            Monitor sync directories for changes"
	@echo "  watch-pdfs       Enhanced file watcher with PDF support"
	@echo "  sync-and-ingest  Run sync tools and ingest content"
	@echo ""
	@echo "🧠 Evolution Commands:"
	@echo "  evolution-status Check Clever's current intelligence level"
	@echo "  trigger-evolution Force evolution cascade"
	@echo "  evolution-learn  Learn from all sync folder content"
	@echo ""
	@echo "⚡ Memory Optimization:"
	@echo "  disable-pylance  Disable Pylance to save memory"
	@echo "  memory-status    Check hardware profile and memory status"
	@echo "  memory-optimize  Apply hardware-aware optimization"
	@echo "  memory-monitor   Start continuous hardware monitoring"
	@echo ""
	@echo "🔧 Maintenance:"
	@echo "  freeze           Generate requirements-lock.txt"
	@echo "  clean-venv       Remove virtual environment"

# Disable Pylance for memory optimization
disable-pylance:
	@echo "⚡ Disabling Pylance for memory optimization..."
	@./disable_pylance.sh
