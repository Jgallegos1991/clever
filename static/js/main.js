/*
main.js - Clever Digital Brain Extension Main Application Logic

Why: Central JavaScript controller orchestrating Clever's cognitive interface initialization,
     particle system management, and user interaction handling for the digital brain extension
     experience. It ensures the UI emerges from Clever's particles (no DOM fallbacks), aligning
     with the vision of Clever as a single coherent cognitive partner.

Where: Loaded by templates/index.html as the primary frontend script after engine dependencies.
       Core frontend component of Clever's cognitive enhancement interface.

How: Coordinates the particle engine, chat flow, and user interactions through modular integration,
     local API calls, and state management. Enforces offline operation and single-user context.

File Usage:
    - Frontend initialization: Primary script for initializing Clever cognitive interface
    - User interaction: Handles user input and particle-formed chat interface
    - Particle coordination: Manages holographic particle system lifecycle
    - State management: Maintains application state and cognitive status
    - API communication: Local-only requests to Flask backend for Clever responses
    - Performance monitoring: Hooks for introspection and status overlay
    - Component orchestration: Coordinates all frontend modules

Connects to:
    - templates/index.html: Script loaded after DOM parsing for initialization
    - static/js/engines/holographic-chamber.js: window.startHolographicChamber() for particle system
    - static/js/core/, static/js/performance/: Optional supporting modules
    - static/css/style.css: Canvas and control styling
    - app.py: Local endpoints (/api/chat, /api/generate_shape, /api/available_shapes)
    - persona.py: Backend personality engine and response modes (server-side)
    - evolution_engine.py: Interaction logging (server-side)
    - debug_config.py + introspection.py: Runtime status overlay (optional)

Performance Notes:
    - Memory usage: Lightweight in-browser state; particle counts controlled by engine
    - CPU impact: Animation loop driven by requestAnimationFrame in engine; avoid heavy work in main thread
    - I/O operations: Local-only fetch calls; no external network access
    - Scaling limits: Single-user UI; tuned for the target device specs in docs/config/device_specifications.md

Critical Dependencies:
    - Required: window.startHolographicChamber() (from holographic-chamber.js)
    - Optional: window.createCognitiveStatusOverlay(), window.toggleCognitiveStatus()
    - System: Modern browser with canvas support; offline operation required
*/

console.log('🧠 Clever Digital Brain Extension initializing...');

// Global state management for cognitive interface
let holographicChamber = null;
let isProcessingMessage = false;
let cognitiveMaintenanceInterval = null;
let lastInteractionTime = Date.now(); // Shared interaction timestamp for cognitive state management
let messagePersistenceEnabled = false; // Toggle for keeping messages visible longer
let lastSubmitAt = 0; // Debounce guard to avoid double-submits
let backgroundPointerFocusHandler = null; // Global pointer handler to recover input focus

/**
 * Toggle Message Persistence
 * 
 * Why: Allow user control over message visibility for better reading experience
 * Where: Toggled via keyboard shortcut or can be called programmatically
 * How: Modifies chat bubble behavior to keep messages visible longer
 */
function toggleMessagePersistence() {
    messagePersistenceEnabled = !messagePersistenceEnabled;
    const status = messagePersistenceEnabled ? 'enabled' : 'disabled';
    console.log(`💬 Message persistence ${status}`);
    showSystemMessage(`Message persistence ${status} - messages will ${messagePersistenceEnabled ? 'stay visible longer' : 'fade normally'}`);
    
    // Update chat config if available (no DOM fallback required)
    // @ts-ignore - optional global provided by legacy component if present
    if (window.CHAT_CONFIG) {
        // @ts-ignore - dynamic property on global window
        window.CHAT_CONFIG.PERSISTENCE_MODE = messagePersistenceEnabled;
    }
}

/**
 * Process Clever's Interface Commands
 * 
 * Why: Allow Clever to control her own interface features and settings
 * Where: Called when Clever sends interface control commands in her responses
 * How: Processes command objects and executes the requested interface actions
 * 
 * @param {object} command - Interface command from Clever
 */
function processCleverInterfaceCommand(command) {
    if (!command || typeof command !== 'object') return;
    
    console.log('🎛️ Processing Clever interface command:', command);
    
    switch (command.type) {
        case 'toggle_persistence':
            toggleMessagePersistence();
            if (command.notify && !messagePersistenceEnabled) {
                console.log('🤖 Clever toggled message persistence');
            }
            break;
        case 'clear_chat':
            if (typeof window.clearChatMessages === 'function') {
                window.clearChatMessages();
                console.log('🤖 Clever cleared the chat');
            }
            break;
        case 'set_cognitive_mode':
            if (command.mode && holographicChamber && typeof holographicChamber.setMode === 'function') {
                holographicChamber.setMode(command.mode);
                console.log(`🤖 Clever set cognitive mode to: ${command.mode}`);
            }
            break;
        default:
            console.warn('🤖 Unknown Clever interface command:', command.type);
    }
}

// Timing constants for chat bubble lifecycle management
/*
Why: Centralized timing ensures consistent cognitive rhythm and easy tuning
Where: Used by particle-created bubbles for message flow
How: Single source of truth mirrored by CSS variables for visual consistency
*/
const BUBBLE_FADE_IN_MS = 500;
const BUBBLE_VISIBLE_MS = 6000; // base visible window before fade
const BUBBLE_FADE_OUT_MS = 1000;

// Cognitive maintenance constants
const COGNITIVE_MAINTENANCE_INTERVAL = 5000; // 5 seconds
const IDLE_OBSERVATION_INTERVAL = 30000; // 30 seconds

/**
 * Start Cognitive Maintenance Loop
 * 
 * Why: Ensures Clever maintains continuous cognitive processing and connection awareness
 * Where: Called after particle system initialization to maintain system coherence
 * How: Periodic monitoring of cognitive state with automatic adjustments and observations
 * 
 * Connects to:
 *     - static/js/engines/holographic-chamber.js: Calls maintainCognitiveConnection()
 *     - app.py: Reports cognitive status for system monitoring
 *     - evolution_engine.py: Logs cognitive patterns for learning
 */
function startCognitiveMaintenanceLoop() {
    if (cognitiveMaintenanceInterval) {
        clearInterval(cognitiveMaintenanceInterval);
    }
    
    cognitiveMaintenanceInterval = setInterval(() => {
        if (!holographicChamber) return;
        
        try {
            // Maintain cognitive connection with error handling
            const cognitiveStatus = holographicChamber.maintainCognitiveConnection();
            
            // Log cognitive health for debugging
            console.log('🧠 Cognitive Status:', {
                coherence: Math.round(cognitiveStatus.coherence * 100) + '%',
                energy: Math.round(cognitiveStatus.energy * 100) + '%',
                mode: cognitiveStatus.mode
            });
            
            // Switch to observing mode during extended idle periods
            const now = Date.now();
            const timeSinceLastInteraction = now - lastInteractionTime;
            
            if (timeSinceLastInteraction > IDLE_OBSERVATION_INTERVAL && 
                holographicChamber.currentMode === 'idle') {
                holographicChamber.setMode('observing');
                console.log('🔍 Entered observation mode - Clever is actively observing');
            }
            
            // Return to idle if recently active
            if (timeSinceLastInteraction < IDLE_OBSERVATION_INTERVAL && 
                holographicChamber.currentMode === 'observing') {
                holographicChamber.setMode('idle');
            }
            
        } catch (error) {
            console.error('❌ Cognitive maintenance error:', error);
            // Continue maintenance even if individual operations fail
        }
        
    }, COGNITIVE_MAINTENANCE_INTERVAL);
    
    console.log('🧠 Cognitive maintenance loop started - Clever will maintain full connection');
}

/**
 * Update Last Interaction Time
 * 
 * Why: Tracks user interaction for cognitive mode management
 * Where: Called by chat interface and other interaction handlers
 * How: Updates timestamp to manage idle/observation state transitions
 */
function updateLastInteraction() {
    if (holographicChamber && holographicChamber.currentMode === 'observing') {
        holographicChamber.setMode('idle');
    }
    lastInteractionTime = Date.now();
}

/**
 * Attach background pointer routing so stage clicks focus the hidden input
 *
 * Why: Canvas uses pointer-events: none, so focus recovery must listen on a target that
 *      actually receives pointer events (e.g., body/html). This keeps keyboard access intact
 *      when the visible DOM input is hidden by particle UI.
 * Where: Called after particle system initialization to ensure the handler exists once.
 * How: Listens for primary pointer interactions on stage elements and forwards focus to input.
 */
function attachBackgroundPointerFocus() {
    if (backgroundPointerFocusHandler) return;

    backgroundPointerFocusHandler = (event) => {
        if (event.defaultPrevented || event.isPrimary === false) return;

        const chatInput = /** @type {HTMLInputElement | null} */ (document.getElementById('chat-input'));
        if (!chatInput) return;

        const rawTarget = /** @type {EventTarget | null} */ (event.target);
        const targetElement = rawTarget && rawTarget instanceof Element
            ? rawTarget
            : (rawTarget && /** @type {Node} */ (rawTarget).parentElement) || null;

        if (!targetElement) return;

        const isStageClick =
            targetElement === document.body ||
            targetElement === document.documentElement ||
            targetElement.id === 'particles' ||
            !!targetElement.closest('.floating-input');

        if (!isStageClick) return;

        if (typeof targetElement.closest === 'function') {
            const interactive = targetElement.closest('button, input, textarea, select, a[href], [role="button"], [contenteditable="true"], [tabindex]:not([tabindex="-1"])');
            if (interactive && interactive !== chatInput) {
                return;
            }
        }

        updateLastInteraction();
        chatInput.focus({ preventScroll: true });

        if (holographicChamber && typeof holographicChamber.setInputBarVisible === 'function') {
            holographicChamber.setInputBarVisible(true);
        }
        if (holographicChamber && typeof holographicChamber.setInputBarFocusState === 'function') {
            holographicChamber.setInputBarFocusState(true);
        }
    };

    document.addEventListener('pointerdown', backgroundPointerFocusHandler, { capture: true });
}

/**
 * Initialize Particle System
 * 
 * Why: Start Clever cognitive visualization representing brain activity
 * Where: Called during DOMContentLoaded to establish visual foundation
 * How: Targets canvas element and initializes HolographicChamber engine
 * 
 * Connects to:
 *     - static/js/engines/holographic-chamber.js: window.startHolographicChamber() function
 *     - templates/index.html: Canvas element with id="particles"
 *     - static/css/style.css: Canvas positioning and styling
 */
function initializeParticleSystem() {
    console.log('🧠 Initializing particle system...');
    const canvas = document.getElementById('particles');
    if (!canvas) {
        console.error('❌ Particles canvas not found - cognitive visualization unavailable');
        return;
    }

    // Cast to HTMLCanvasElement for proper typing
    const canvasElement = /** @type {HTMLCanvasElement} */ (canvas);
    
    // Set canvas dimensions to viewport
    canvasElement.width = window.innerWidth;
    canvasElement.height = window.innerHeight;

    // Initialize holographic chamber if engine is available
    if (typeof window.startHolographicChamber === 'function') {
        holographicChamber = window.startHolographicChamber(canvasElement);
        if (holographicChamber) {
            holographicChamber.animate();
            startCognitiveMaintenanceLoop();

            // Hide DOM chat fallback when particle system is active
            const fallbackLog = document.getElementById('chat-log');
            if (fallbackLog) {
                fallbackLog.style.display = 'none';
            }

            // Create/show particle-formed input bar
            if (typeof holographicChamber.ensureInputBar === 'function') {
                holographicChamber.ensureInputBar();
            }
            if (typeof holographicChamber.setInputBarVisible === 'function') {
                holographicChamber.setInputBarVisible(true);
            }
            
            // Mark body as particles-active so CSS can hide DOM input visually
            document.body.classList.add('particles-active');
            attachBackgroundPointerFocus();
        } else {
            console.error('❌ Failed to initialize holographic chamber');
        }
    } else {
        console.error('❌ Holographic chamber engine not loaded');
        console.log('Available window functions:', Object.keys(window).filter(k => k.includes('Chamber')));
    }

    // Handle window resize for responsive particle system
    window.addEventListener('resize', () => {
        canvasElement.width = window.innerWidth;
        canvasElement.height = window.innerHeight;
        if (holographicChamber && typeof holographicChamber.resize === 'function') {
            holographicChamber.resize(canvasElement.width, canvasElement.height);
        }
    });
}

/**
 * Initialize Chat Interface
 * 
 * Why: Set up conversation system for cognitive partnership with Clever
 * Where: Called during DOMContentLoaded to enable user interaction
 * How: Event handlers for form submission, keyboard shortcuts, and message processing
 * 
 * Connects to:
 *     - templates/index.html: Form element with id="chat-form"
 *     - app.py: /api/chat endpoint for message processing (local only)
 *     - static/css/style.css: Any styling hooks for visibility toggles
 */
function initializeChatInterface() {
    console.log('💬 Initializing chat interface...');
    const chatForm = document.getElementById('chat-form');
    const chatInput = /** @type {HTMLInputElement} */ (document.getElementById('chat-input'));
    const sendButton = document.getElementById('send-btn');

    if (!chatForm || !chatInput || !sendButton) {
        console.error('❌ Chat interface elements not found');
        return;
    }

    // Visual hiding is handled by CSS body.particles-active rules; no inline style changes here

    // Handle form submission (guarded against duplicates)
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleMessageSubmit();
    });

    // Handle send button click
    sendButton.addEventListener('click', async (e) => {
        e.preventDefault();
        await handleMessageSubmit();
    });

    // Keyboard shortcuts for enhanced interaction and single Enter-submit (only when focused)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey && document.activeElement === chatInput) {
            e.preventDefault();
            handleMessageSubmit();
        }
        
        // Particle mode shortcuts
        if (e.shiftKey && holographicChamber) {
            switch (e.key.toLowerCase()) {
                case 'c':
                    e.preventDefault();
                    updateLastInteraction();
                    holographicChamber.setMode('creative');
                    showSystemMessage('🎨 Creative mode activated');
                    break;
                case 's':
                    e.preventDefault();
                    updateLastInteraction();
                    holographicChamber.setMode('thinking');
                    showSystemMessage('🧠 Thinking mode activated');
                    break;
                case 'i':
                    e.preventDefault();
                    updateLastInteraction();
                    holographicChamber.setMode('idle');
                    showSystemMessage('😌 Idle mode activated');
                    break;
            }
        }
    });

    // Mirror input text into particle-formed input bar
    chatInput.addEventListener('input', () => {
        if (holographicChamber && typeof holographicChamber.updateInputBarText === 'function') {
            holographicChamber.updateInputBarText(chatInput.value);
        }
    });

    // Ensure input bar visible on focus
    chatInput.addEventListener('focus', () => {
        if (!holographicChamber) return;
        if (typeof holographicChamber.setInputBarVisible === 'function') {
            holographicChamber.setInputBarVisible(true);
        }
        if (typeof holographicChamber.setInputBarFocusState === 'function') {
            holographicChamber.setInputBarFocusState(true);
        }
    });

    chatInput.addEventListener('blur', () => {
        if (holographicChamber && typeof holographicChamber.setInputBarFocusState === 'function') {
            holographicChamber.setInputBarFocusState(false);
        }
    });
}

/**
 * Handle Message Submit
 * 
 * Why: Process user input and communicate with Clever's cognitive engine
 * Where: Called by form submit and send button events
 * How: Validate input, send to API, display response with particle-based UI
 * 
 * Connects to:
 *     - app.py: POST request to /api/chat endpoint (local only)
 *     - persona.py: Backend processing of user message
 */
async function handleMessageSubmit() {
    const nowTs = Date.now();
    // Debounce rapid double-fires (keydown + submit) within 250ms
    if (nowTs - lastSubmitAt < 250) {
        return;
    }
    if (isProcessingMessage) {
        console.log('⏳ Message already processing...');
        return;
    }

    const chatInput = /** @type {HTMLInputElement} */ (document.getElementById('chat-input'));
    const message = chatInput.value.trim();

    if (!message) {
        console.log('❌ Empty message - nothing to send');
        return;
    }

    isProcessingMessage = true;
    lastSubmitAt = nowTs;
    
    try {
        // Update interaction tracking for cognitive maintenance
        updateLastInteraction();

        // Shape command detection BEFORE chat routing
        const lower = message.toLowerCase();
        const shapeTriggers = ['form', 'draw', 'make', 'generate', 'create'];
        const shapeWords = ['cone', 'cube', 'sphere', 'torus', 'helix'];
        const startsWithTrigger = shapeTriggers.some(t => lower.startsWith(t + ' '));
        const containsShapeWord = shapeWords.some(w => lower.includes(w));

        if (startsWithTrigger && containsShapeWord) {
            console.log('🎨 Shape command detected:', message);
            // Clear input and mirror to particle bar
            chatInput.value = '';
            if (holographicChamber && typeof holographicChamber.updateInputBarText === 'function') {
                holographicChamber.updateInputBarText('');
            }
            if (holographicChamber && typeof holographicChamber.setMode === 'function') {
                holographicChamber.setMode('creative');
            }

            // Extract first matching shape word as the type
            const shapeType = shapeWords.find(w => lower.includes(w)) || 'sphere';

            // Route to shape generation API instead of chat
            const resp = await fetch('/api/generate_shape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ shape: shapeType })
            });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
            const result = await resp.json();

            const shapeData = (result && (result.shape || result.data || null));
            console.log('🧩 Shape data received:', shapeData);
            if (holographicChamber && shapeData) {
                if (typeof holographicChamber.createShapeFromData === 'function') {
                    holographicChamber.createShapeFromData(shapeData);
                } else if (typeof holographicChamber.createMathematicalShape === 'function') {
                    // Back-compat: try to adapt structure minimally
                    holographicChamber.createMathematicalShape({ name: shapeData.type || 'shape', properties: {}, points: [] });
                }
                // Transition to observing after a brief showcase
                setTimeout(() => {
                    if (holographicChamber && typeof holographicChamber.setMode === 'function') {
                        holographicChamber.setMode('observing');
                    }
                }, 6000);
            }
            return; // Do not produce chat panels for shape commands
        }

        // Display user message (only for non-shape messages)
        displayMessage(message, 'user');
        chatInput.value = '';
        if (holographicChamber && typeof holographicChamber.updateInputBarText === 'function') {
            holographicChamber.updateInputBarText('');
        }

        // Set thinking mode if particle system available
        if (holographicChamber && typeof holographicChamber.setMode === 'function') {
            holographicChamber.setMode('thinking');
        }

        // Send message to Clever's cognitive engine (local-only)
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        // Process mathematical shape data if present
        if (data.shape_data && holographicChamber && typeof holographicChamber.createMathematicalShape === 'function') {
            holographicChamber.createMathematicalShape(data.shape_data);
            holographicChamber.setMode('creative');
            setTimeout(() => {
                if (holographicChamber && typeof holographicChamber.startShapeRotation === 'function') {
                    holographicChamber.startShapeRotation();
                }
            }, 1000);
            setTimeout(() => {
                if (holographicChamber && typeof holographicChamber.setMode === 'function') {
                    holographicChamber.setMode('observing');
                }
            }, 10000);
        }
        // Handle legacy particle commands if present
        else if (data.requested_shape && holographicChamber) {
            const shapeMap = {
                'cube': 'createCubeFormation',
                'sphere': 'createSphereFormation', 
                'torus': 'createTorusFormation',
                'helix': 'createHelixFormation',
                'spiral': 'createHelixFormation',
                'constellation': 'createConstellationFormation'
            };
            const formationMethod = shapeMap[data.requested_shape];
            if (formationMethod && typeof holographicChamber[formationMethod] === 'function') {
                holographicChamber[formationMethod]();
                holographicChamber.setMode('creative');
                setTimeout(() => {
                    if (holographicChamber && typeof holographicChamber.setMode === 'function') {
                        holographicChamber.setMode('idle');
                    }
                }, 2000);
            }
        }
        
        // Process interface commands from Clever
        if (data.frontend_command) {
            processCleverInterfaceCommand(data.frontend_command);
        }
        
        // Display Clever's response with knowledge domain detection
        if (data.response) {
            const knowledgeDomain = data.knowledge_domain || data.analysis?.knowledge_domain;
            const mood = data.analysis?.mood || data.mood || 'neutral';
            displayMessage(data.response, 'clever', knowledgeDomain, mood);
        } else {
            console.error('❌ No response in API data:', data);
            showSystemMessage('❌ No response received from Clever');
        }

        // Return to idle mode if no shape processing occurred
        if (!data.shape_data && !data.requested_shape && holographicChamber && typeof holographicChamber.setMode === 'function') {
            holographicChamber.setMode('idle');
        }

    } catch (error) {
        console.error('❌ Chat error:', error);
        showSystemMessage(`❌ Error: ${error.message}`);
        
        // Return to idle mode on error
        if (holographicChamber && typeof holographicChamber.setMode === 'function') {
            holographicChamber.setMode('idle');
        }
    } finally {
        isProcessingMessage = false;
    }
}

/**
 * Display Message using Particle-Based UI
 * 
 * Why: Show messages through dynamic particle formations instead of static HTML
 * Where: Called when displaying user or AI messages in chat interface
 * How: Uses holographic chamber to create particle-formed chat bubbles with knowledge-driven colors
 * 
 * Connects to:
 *     - static/js/engines/holographic-chamber.js: createParticleChatBubble() for dynamic UI
 *     - persona.py: Knowledge domain detection drives particle colors and formations
 */
function displayMessage(text, sender = 'system', knowledgeDomain = null, mood = 'neutral') {
    console.log(`📢 displayMessage called: "${text}" from ${sender}`);
    
    // Use particle-formed chat bubbles for dynamic UI (no DOM fallback)
    if (holographicChamber && typeof holographicChamber.createParticleChatBubble === 'function') {
        if (!knowledgeDomain) {
            knowledgeDomain = detectKnowledgeDomain(text);
        }
        // Compute dynamic on-screen duration based on message length
        // Base: 6s, Scale: ~200ms/char, Max: 20s; boost 30% if persistence enabled
        const len = Math.max(1, String(text || '').length);
        const dynamicVisible = Math.min(20000, Math.max(6000, Math.round(len * 200)));
        const finalVisible = Math.min(30000, Math.round(dynamicVisible * (messagePersistenceEnabled ? 1.3 : 1.0)));

        // Temporarily set global for engine to consume at creation time
        const prevVisible = /** @type {any} */ (globalThis).BUBBLE_VISIBLE_MS;
        /** @type {any} */ (globalThis).BUBBLE_VISIBLE_MS = finalVisible;

    const bubbleId = holographicChamber.createParticleChatBubble(text, sender, knowledgeDomain, mood);

        // Restore previous global to avoid affecting subsequent bubbles
        /** @type {any} */ (globalThis).BUBBLE_VISIBLE_MS = prevVisible ?? 6000;

        if (knowledgeDomain && typeof holographicChamber.setKnowledgeMode === 'function') {
            holographicChamber.setKnowledgeMode(knowledgeDomain);
        } else if (typeof holographicChamber.setKnowledgeMode === 'function') {
            holographicChamber.setKnowledgeMode('chat_interface');
        }
        console.log(`🔮 Particle bubble created: ${bubbleId} with ${knowledgeDomain || 'default'} theme`);
        return;
    }
    
    // No fallback: Clever exists as particles; log for diagnostics only
    console.warn('🔮 Particle system unavailable - cannot render message as particles');
    console.log(`${sender.toUpperCase()}: ${text}`);
}

/**
 * Detect Knowledge Domain from Message Content
 * 
 * Why: Automatically determine which knowledge type to visualize with particles
 * Where: Called when creating particle chat bubbles to set appropriate colors
 * How: Keyword analysis and content pattern matching for intelligent knowledge classification
 */
function detectKnowledgeDomain(text) {
    const lowerText = text.toLowerCase();
    
    // Biblical/spiritual knowledge
    if (lowerText.match(/\b(god|jesus|christ|bible|scripture|faith|prayer|salvation|heaven|holy|divine|blessed|amen|lord|almighty)\b/)) {
        return 'biblical_knowledge';
    }
    
    // Mathematics and science
    if (lowerText.match(/\b(math|equation|formula|calculate|physics|science|theory|algorithm|function|variable|solve|proof)\b/)) {
        return 'mathematics_science';
    }
    
    // Programming and technology
    if (lowerText.match(/\b(code|programming|function|variable|javascript|python|html|css|api|database|server|debug)\b/)) {
        return 'programming_knowledge';
    }
    
    // Economics and finance
    if (lowerText.match(/\b(money|economy|finance|business|market|investment|profit|budget|economic|financial|trade)\b/)) {
        return 'economics_knowledge';
    }
    
    // Historical knowledge
    if (lowerText.match(/\b(history|historical|ancient|war|empire|civilization|past|century|era|traditional)\b/)) {
        return 'historical_knowledge';
    }
    
    // Language and literature
    if (lowerText.match(/\b(language|literature|poetry|writing|words|grammar|meaning|story|narrative|linguistic)\b/)) {
        return 'language_arts';
    }
    
    // Default to chat interface theme
    return 'chat_interface';
}

/**
 * Show System Message
 * 
 * Why: Display system notifications and status updates
 * Where: Called for particle mode changes and error notifications
 * How: Uses displayMessage() with system styling
 */
function showSystemMessage(text) {
    displayMessage(text, 'system');
}

/**
 * Initialize Application
 * 
 * Why: Bootstrap Clever's cognitive interface when DOM is ready
 * Where: Event listener for DOMContentLoaded ensures proper initialization order
 * How: Sequential initialization of particle system, chat interface, and cognitive features
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('🧠 Clever Digital Brain Extension - Initializing...');
    
    initializeParticleSystem();
    initializeChatInterface();
    initializeCognitiveStatus();
    initializeKeyboardShortcuts();
    
    console.log('✅ Clever Digital Brain Extension - Ready for cognitive partnership with full connection monitoring');
});

/**
 * Determine whether to auto-focus the hidden input on load
 *
 * Why: Avoid forcing soft keyboard open on touch devices while keeping desktop ready-to-type behavior.
 * Where: Used during window load once DOM elements are available.
 * How: Checks pointer media queries and viewport size to infer mobile/tablet contexts.
 */
function shouldAutoFocusInput() {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
        return true;
    }

    const coarsePointer = window.matchMedia('(pointer: coarse)').matches;
    const finePointer = window.matchMedia('(pointer: fine)').matches;
    const primaryCoarse = coarsePointer && !finePointer;
    const compactViewport = window.innerWidth <= 820;

    return !(primaryCoarse || compactViewport);
}

// Ensure the visible chat input is focused on load
window.addEventListener('load', () => {
    const input = /** @type {HTMLInputElement} */ (document.querySelector('#chat-input'));
    if (!input) return;

    if (shouldAutoFocusInput()) {
        window.requestAnimationFrame(() => {
            input.focus({ preventScroll: true });
        });
    }
});

/**
 * Initialize Cognitive Status Overlay
 * 
 * Why: Provides real-time monitoring of Clever's cognitive health and connection status
 * Where: Called during initialization to establish system monitoring interface
 * How: Creates status overlay and starts monitoring loop for particle system health
 */
function initializeCognitiveStatus() {
    if (typeof window.createCognitiveStatusOverlay === 'function') {
        window.createCognitiveStatusOverlay();
        console.log('✅ Cognitive status monitoring active');
    } else {
        console.warn('⚠️ Cognitive status component not available');
    }
}

/**
 * Generate Mathematical Shape
 * 
 * Why: Direct API interface for mathematical shape generation and visualization
 * Where: Can be called programmatically or via console for shape testing
 * How: Makes API request to shape generator, applies result to particle system
 * 
 * Connects to:
 *     - app.py: POST request to /api/generate_shape endpoint
 *     - shape_generator.py: Backend mathematical shape generation
 *     - holographic-chamber.js: createMathematicalShape() for visualization
 */
async function generateShape(shapeName, options = {}) {
    try {
        console.log(`📐 Generating mathematical shape: ${shapeName}`);
        
        const response = await fetch('/api/generate_shape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                shape: shapeName,
                ...options
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        if (data.success && data.shape) {
            console.log(`✅ Shape generated: ${data.shape.name} with ${data.shape.point_count} points`);
            
            // Apply to particle system if available
            if (holographicChamber && typeof holographicChamber.createMathematicalShape === 'function') {
                holographicChamber.createMathematicalShape(data.shape);
                holographicChamber.setMode('creative');
                
                // Return to observing mode after visualization
                setTimeout(() => {
                    if (holographicChamber && typeof holographicChamber.setMode === 'function') {
                        holographicChamber.setMode('observing');
                    }
                }, 4000);
            }
            
            return data.shape;
        } else {
            throw new Error(data.error || 'Shape generation failed');
        }
        
    } catch (error) {
        console.error('❌ Shape generation error:', error);
        showSystemMessage(`❌ Shape generation failed: ${error.message}`);
        throw error;
    }
}

/**
 * Get Available Shapes
 * 
 * Why: Provides list of available shapes for UI controls and help systems
 * Where: Called by UI components that need shape selection options
 * How: Fetches shape catalog from API with categorized information
 */
async function getAvailableShapes() {
    try {
        const response = await fetch('/api/available_shapes');
        const data = await response.json();
        
        if (data.success) {
            console.log(`📚 Available shapes: ${data.total_shapes} shapes in ${Object.keys(data.categories).length} categories`);
            return data.categories;
        } else {
            throw new Error(data.error || 'Failed to get available shapes');
        }
        
    } catch (error) {
        console.error('❌ Error fetching available shapes:', error);
        return {};
    }
}

// Expose shape functions globally for console access and testing
if (typeof window !== 'undefined') {
    window.generateShape = generateShape;
    window.getAvailableShapes = getAvailableShapes;
}

/**
 * Initialize Keyboard Shortcuts
 * 
 * Why: Provides quick access to cognitive interface controls for power users
 * Where: Called during initialization to establish global keyboard handlers
 * How: Event listeners for key combinations that control cognitive interface features
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Do not hijack typing when input is focused unless using control combos
        const active = document.activeElement;
        const chatInput = /** @type {HTMLInputElement} */ (document.getElementById('chat-input'));
        const inputFocused = (active === chatInput);
        // Ctrl+Shift+S: Toggle cognitive status overlay
        if (e.ctrlKey && e.shiftKey && e.key === 'S') {
            e.preventDefault();
            if (typeof window.toggleCognitiveStatus === 'function') {
                window.toggleCognitiveStatus();
            }
        }
        
        // Ctrl+Shift+O: Switch to observation mode
        if (e.ctrlKey && e.shiftKey && e.key === 'O') {
            e.preventDefault();
            updateLastInteraction();
            if (holographicChamber && typeof holographicChamber.setMode === 'function') {
                holographicChamber.setMode('observing');
                console.log('🔍 Manual observation mode activated');
            }
        }
        
        // Ctrl+Shift+I: Return to idle mode
        if (e.ctrlKey && e.shiftKey && e.key === 'I') {
            e.preventDefault();
            updateLastInteraction();
            if (holographicChamber && typeof holographicChamber.setMode === 'function') {
                holographicChamber.setMode('idle');
                console.log('🧠 Returned to idle cognitive mode');
            }
        }
        
        // Ctrl+Shift+M: Toggle message persistence
        if (e.ctrlKey && e.shiftKey && e.key === 'M') {
            e.preventDefault();
            toggleMessagePersistence();
        }
        
        // Ctrl+Shift+C: Clear all chat messages
        if (e.ctrlKey && e.shiftKey && e.key === 'C') {
            e.preventDefault();
            // Clear particle panels first if engine active
            if (holographicChamber && typeof holographicChamber.clearChatPanels === 'function') {
                const count = holographicChamber.clearChatPanels({ graceful: true });
                console.log(`🧹 Cleared ${count} particle chat panel(s)`);
            }
            // Also clear DOM fallback log if present
            if (typeof window.clearChatMessages === 'function') {
                window.clearChatMessages();
            }
            showSystemMessage('Chat cleared - ready for fresh conversation');
        }
    });
    
    console.log('⌨️ Keyboard shortcuts initialized (Ctrl+Shift+S, O, I, M, C)');
}

// Export for debugging and external access
/*
Why: Provide access to internal state for development and debugging
Where: Available in browser console for runtime inspection
How: Global window properties for key functions and state
*/
 /** @type {any} */ (window).CleverApp = {
    get holographicChamber() { return holographicChamber; },
    get isProcessingMessage() { return isProcessingMessage; },
    displayMessage,
    showSystemMessage,
    updateLastInteraction,
    version: '1.0.0'
};

console.log('📦 Clever main.js loaded and ready');
