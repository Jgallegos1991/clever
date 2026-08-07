/**
 * holographic-chamber.js - Particle System Engine for Clever Cognitive Enhancement Interface
 * 
 * Why: Creates cognitive visualization representing Clever thought processes and mental activity,
 * providing immersive visual feedback that enhances the digital brain extension experience.
 * Essential for making Clever cognitive partnership tangible and engaging through dynamic
 * particle formations that respond to her thinking patterns and user interactions.
 * 
 * Where: Core particle engine loaded by templates/index.html before main.js initialization.
 * Central visual component of Clever cognitive enhancement interface and digital brain extension.
 * 
 * How: Canvas-based particle physics with formation morphing, animations, and cognitive state
 * visualization through dynamic particle behavior and visual themes.
 * 
 * File Usage:
 *     - Cognitive visualization: Primary engine for visualizing Clever thought processes
 *     - User engagement: Creates immersive interface enhancing cognitive partnership experience  
 *     - Performance rendering: Optimized particle system for smooth real-time visualization
 *     - State indication: Visual feedback system for Clever's cognitive and emotional states
 *     - Interactive response: Particle behavior responds to user interactions and system events
 *     - Theme management: Handles multiple visual themes for different cognitive states
 *     - Animation control: Manages complex particle animations and formation transitions
 *     - Hardware optimization: Adapts rendering based on device capabilities and performance
 * 
 * Connects to:
 *     - templates/index.html: Core template loading this engine before main application logic
 *     - static/js/main.js: Main application coordinating particle system lifecycle and control
 *     - static/css/style.css: CSS integration for canvas positioning and responsive design
 *     - app.py: Backend integration for cognitive state updates and particle behavior triggers
 *     - persona.py: Personality engine integration for particle themes matching Clever's moods
 *     - evolution_engine.py: Learning system integration for adaptive particle behavior
 *     - docs/config/device_specifications.md: Hardware constraints defining particle count limits
 *     - debug_config.py: Performance monitoring and optimization for particle rendering
 *     - cognitive_shape_engine.py: Advanced shape generation integration for complex formations
 */

console.log('🌟 Holographic Chamber engine loading...');

// Configuration constants
const PARTICLE_CONFIG = {
    MAX_PARTICLES: 100,
    PARTICLE_SIZE: 2,
    ANIMATION_SPEED: 0.8,
    ENERGY_DECAY: 0.98
};

// Visual themes
const VISUAL_THEMES = {
    idle: {
        colors: ['#00FFFF', '#4A9EFF', '#00BFFF'],
        energy: 0.4,
        formation: 'rotating_sphere',
        pulse: true
    },
    thinking: {
        colors: ['#00FF88', '#00FFFF', '#88FFFF'],
        energy: 0.7,
        formation: 'helix',
        pulse: false
    },
    creative: {
        colors: ['#FF6B9D', '#C44569', '#F8B500'],
        energy: 0.9,
        formation: 'constellation',
        pulse: false
    },
    observing: {
        colors: ['#FFD700', '#FFA500', '#FF8C00'],
        energy: 0.6,
        formation: 'rotating_sphere',
        pulse: true
    },
    // Knowledge Domain Color Themes for Intelligent Particle Visualization
    biblical_knowledge: {
        colors: ['#FFD700', '#FFF8DC', '#F0E68C'], // Divine gold wisdom
        energy: 0.8,
        formation: 'sacred_geometry',
        pulse: true
    },
    mathematics_science: {
        colors: ['#00CED1', '#20B2AA', '#48D1CC'], // Mathematical precision cyan
        energy: 0.9,
        formation: 'geometric_patterns',
        pulse: false
    },
    programming_knowledge: {
        colors: ['#32CD32', '#98FB98', '#90EE90'], // Code matrix green
        energy: 0.85,
        formation: 'data_streams',
        pulse: false
    },
    economics_knowledge: {
        colors: ['#DAA520', '#B8860B', '#CD853F'], // Economic gold
        energy: 0.7,
        formation: 'network_web',
        pulse: true
    },
    historical_knowledge: {
        colors: ['#8B4513', '#A0522D', '#D2691E'], // Ancient wisdom bronze
        energy: 0.6,
        formation: 'timeline_flow',
        pulse: true
    },
    language_arts: {
        colors: ['#9370DB', '#BA55D3', '#DA70D6'], // Literary purple
        energy: 0.75,
        formation: 'word_clusters',
        pulse: false
    },
    chat_interface: {
        colors: ['#69EACB', '#4ECDC4', '#45B7D1'], // Clever's signature cyan
        energy: 0.6,
        formation: 'chat_bubble',
        pulse: false
    }
};

/**
 * Particle Class - Individual cognitive elements
 */
class Particle {
    constructor(x, y, chamber) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 2;
        this.vy = (Math.random() - 0.5) * 2;
        this.size = PARTICLE_CONFIG.PARTICLE_SIZE + Math.random();
        this.energy = Math.random() * 0.5 + 0.5;
        this.chamber = chamber;
        
        // Formation properties
        this.targetX = x;
        this.targetY = y;
        this.formationStrength = 0.1;
        this.isInFormation = false;
        
        // Rotation properties for idle state
        this.rotationAngle = Math.random() * Math.PI * 2;
        this.rotationRadius = 0;
        this.baseX = x;
        this.baseY = y;
        this.rotationSpeed = (Math.random() - 0.5) * 0.02;
        
        // Visual properties
        this.opacity = Math.random() * 0.5 + 0.5;
        // Provide a default color so renderers relying on particle.color are safe
        this.color = (VISUAL_THEMES.chat_interface && VISUAL_THEMES.chat_interface.colors[0]) || '#69EACB';
        this.colorIndex = Math.floor(Math.random() * 3);
        this.pulsePhase = Math.random() * Math.PI * 2;
        this.basePulse = Math.random() * 0.3 + 0.7;
        
        // Mathematical properties
        this.mathematicalPoint = false; // Flag for mathematical shape precision

        // UI/Recruitment auxiliary properties (declared to satisfy static analysis)
        this.isRecruited = false;
        this.originalX = x;
        this.originalY = y;
        this.originalColor = this.color;
        this.originalSize = this.size;
        this.dynamicPanel = false;
    }
    
    update() {
        // Update rotation angle for continuous movement
        this.rotationAngle += this.rotationSpeed;
        
        // Formation behavior
        if (this.isInFormation) {
            const dx = this.targetX - this.x;
            const dy = this.targetY - this.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 1) {
                // Enhanced formation strength for mathematical shapes
                const baseStrength = this.mathematicalPoint ? 0.05 : 0.01;
                this.vx += dx * this.formationStrength * baseStrength;
                this.vy += dy * this.formationStrength * baseStrength;
                
                // Additional direct movement for mathematical precision
                if (this.mathematicalPoint && distance > 5) {
                    this.vx += dx * 0.008;
                    this.vy += dy * 0.008;
                }
            }
            
            // Add rotation to formation targets for rotating formations (but not mathematical shapes)
            if (this.chamber.currentFormation === 'rotating_sphere' && !this.mathematicalPoint) {
                this.targetX += Math.cos(this.rotationAngle) * 0.5;
                this.targetY += Math.sin(this.rotationAngle) * 0.5;
            }
        }
        
        // Free movement with subtle rotation
        if (!this.isInFormation) {
            // Add rotational movement around base position
            const rotX = Math.cos(this.rotationAngle) * this.rotationRadius;
            const rotY = Math.sin(this.rotationAngle) * this.rotationRadius;
            
            this.vx += (Math.random() - 0.5) * 0.02;
            this.vy += (Math.random() - 0.5) * 0.02;
            
            // Subtle gravitational pull towards rotation center
            this.vx += (rotX * 0.001);
            this.vy += (rotY * 0.001);
        }
        
        // Apply velocity
        this.x += this.vx * PARTICLE_CONFIG.ANIMATION_SPEED;
        this.y += this.vy * PARTICLE_CONFIG.ANIMATION_SPEED;
        this.vx *= PARTICLE_CONFIG.ENERGY_DECAY;
        this.vy *= PARTICLE_CONFIG.ENERGY_DECAY;
        
        // Boundary conditions
        const canvas = this.chamber.canvas;
        const margin = 20;
        
        if (this.x < margin) {
            this.x = margin;
            this.vx = Math.abs(this.vx) * 0.5;
        }
        if (this.x > canvas.width - margin) {
            this.x = canvas.width - margin;
            this.vx = -Math.abs(this.vx) * 0.5;
        }
        if (this.y < margin) {
            this.y = margin;
            this.vy = Math.abs(this.vy) * 0.5;
        }
        if (this.y > canvas.height - margin) {
            this.y = canvas.height - margin;
            this.vy = -Math.abs(this.vy) * 0.5;
        }
        
        // Update energy
        this.energy = Math.max(0.1, this.energy * 0.999 + Math.random() * 0.001);
        this.opacity = this.energy * 0.8 + 0.2;
    }
    
    render(ctx) {
        const theme = VISUAL_THEMES[this.chamber.currentMode] || VISUAL_THEMES.idle;
        const color = theme.colors[this.colorIndex % theme.colors.length];
        
        // Calculate pulse effect if enabled
        let pulseMultiplier = 1;
        if (theme.pulse) {
            this.pulsePhase += 0.05;
            pulseMultiplier = this.basePulse + Math.sin(this.pulsePhase) * 0.3;
        }
        
        ctx.save();
        
        // Apply pulsing opacity and size
        ctx.globalAlpha = this.opacity * pulseMultiplier;
        const renderSize = this.size * pulseMultiplier;
        
        // Create glow effect
        const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, renderSize * 2);
        gradient.addColorStop(0, color);
        gradient.addColorStop(0.5, color + '80'); // Semi-transparent
        gradient.addColorStop(1, color + '00'); // Fully transparent
        
        // Draw glow
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(this.x, this.y, renderSize * 2, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw core particle
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, renderSize, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.restore();
    }
    
    /**
     * Calculate distance to another particle
     * 
     * Why: Needed for connection line rendering between nearby particles
     * Where: Called by HolographicChamber.renderConnections() for proximity detection
     * How: Uses Euclidean distance formula for accurate spatial relationships
     */
    distanceTo(other) {
        const dx = this.x - other.x;
        const dy = this.y - other.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
}


/**
 * Holographic Chamber Main Class
 */
class HolographicChamber {
    /**
     * getDomainColor - Wrapper for domain/mood palette and glow/pulse
     * 
     * Why: Provide a compact, explicit helper as requested for palette + glow
     * Where: Used by chat panel creation to set colors and glow intensity
     * How: Delegates to getDomainVisuals and returns { colors, glow, pulseProfile }
     */
    getDomainColor(knowledgeDomain = 'chat_interface', mood = 'neutral') {
        const visuals = this.getDomainVisuals(knowledgeDomain, mood);
        return {
            colors: visuals.colors.slice(),
            glow: visuals.energy, // glow is mapped to energy target
            pulseProfile: visuals.pulseProfile,
        };
    }
    /**
     * Get domain visuals (colors, energy, pulse profile) for a knowledge domain and mood
     * 
     * Why: Visual tone-of-voice—color and motion patterns match cognitive context
     * Where: Used by panel creation and animation to drive palette and pulse style
     * How: Returns { colors, energy, pulseProfile } given domain + mood
     */
    getDomainVisuals(knowledgeDomain = 'chat_interface', mood = 'neutral') {
        // Base presets per domain
        const presets = {
            mathematics_science: { colors: ['#00E5FF', '#00B2FF', '#3DD5FF'], energy: 0.75, pulse: 'tight' }, // cyan/electric blue, tight pulse
            programming_knowledge: { colors: ['#7CFF00', '#A8FF3D', '#66CC00'], energy: 0.65, pulse: 'staccato' }, // lime green, micro-pulses
            biblical_knowledge: { colors: ['#FFD166', '#FFB703', '#F4A261'], energy: 0.5, pulse: 'bloom' }, // gold, slow radiant bloom
            language_arts: { colors: ['#FF5EC4', '#D946EF', '#A21CAF'], energy: 0.6, pulse: 'wave' }, // magenta, wave-like oscillation
            economics_knowledge: { colors: ['#56E39F', '#2BB673', '#13C4A3'], energy: 0.6, pulse: 'steady' },
            historical_knowledge: { colors: ['#F2C14E', '#E27D60', '#C38D9E'], energy: 0.55, pulse: 'swell' },
            chat_interface: { colors: ['#B3E5FC', '#81D4FA', '#E1F5FE'], energy: 0.5, pulse: 'neutral' }, // soft blue-white
        };

        const base = presets[knowledgeDomain] || presets.chat_interface;

        // Mood modulation adjusts energy and pulse subtly
        const moodMods = {
            excited: 1.2,
            confident: 1.1,
            thoughtful: 0.9,
            calm: 0.85,
            neutral: 1.0,
        };
        const energyScale = moodMods[mood] || 1.0;

        // Pulse profile descriptor
        const pulseProfiles = {
            tight: { speed: 0.1, amplitude: 0.6, jitter: 0.02 },
            staccato: { speed: 0.16, amplitude: 0.35, jitter: 0.08 },
            bloom: { speed: 0.055, amplitude: 0.7, jitter: 0.01 },
            wave: { speed: 0.075, amplitude: 0.55, jitter: 0.03 },
            swell: { speed: 0.065, amplitude: 0.45, jitter: 0.02 },
            steady: { speed: 0.06, amplitude: 0.35, jitter: 0.015 },
            neutral: { speed: 0.08, amplitude: 0.4, jitter: 0.02 },
        };

        const profile = pulseProfiles[base.pulse] || pulseProfiles.neutral;
        return {
            colors: base.colors,
            energy: base.energy * energyScale,
            pulseProfile: profile,
        };
    }
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.particles = [];
        this.currentMode = 'idle';
        this.currentFormation = 'sphere';
        this.isAnimating = false;
        this.animationId = null;
        
        // Shape rotation properties
        this.currentShapeData = null;
        this.isRotatingShape = false;
        
        // DYNAMIC UI CREATION SYSTEM
        this.uiElements = new Map(); // Track particle-formed UI elements
        this.knowledgeColors = VISUAL_THEMES; // Access to knowledge-driven colors
        this.activeKnowledgeDomain = null; // Current knowledge type affecting particles

        // Why: Maintain conversational ordering to connect particle-formed chat panels
        // Where: Used by renderChatFlowConnections() to draw intelligent links between messages
        // How: Append bubbleId on creation and prune non-existent IDs during rendering
        this.chatBubbleOrder = [];
    // Diagnostics and performance tracking
    this._diagnosticsEnabled = false;
    this._lastFrameTs = performance.now();
    this._fpsEMA = 60; // start optimistic
    this._lastPanelProfile = null;
    this._lastPanelContext = { domain: 'chat_interface', mood: 'neutral' };

    // Particle-formed input bar state
    this.inputBarId = null; // UI element key for input bar in uiElements
    this.inputBarText = '';
    this.inputBarVisible = false;
    this.inputCaretBlink = 0;
    this.inputBarFocus = false;
    this.inputBarFocusTarget = 0;
        
        this.createParticles();
        console.log('Chamber initialized with', this.particles.length, 'particles and dynamic UI capabilities');
    }
    
    createParticles() {
        this.particles = [];
        const particleCount = 60; // REVERTED: Keep original count to maintain UI stability
        
        for (let i = 0; i < particleCount; i++) {
            const angle = (i / particleCount) * Math.PI * 2;
            const radius = Math.random() * Math.min(this.canvas.width, this.canvas.height) * 0.3;
            const centerX = this.canvas.width / 2;
            const centerY = this.canvas.height / 2;
            
            const x = centerX + Math.cos(angle) * radius + (Math.random() - 0.5) * 100;
            const y = centerY + Math.sin(angle) * radius + (Math.random() - 0.5) * 100;
            
            this.particles.push(new Particle(x, y, this));
        }
    }
    
    setMode(mode) {
        if (VISUAL_THEMES[mode]) {
            console.log('🧠 Cognitive mode transition:', this.currentMode, '->', mode);
            this.currentMode = mode;
            const theme = VISUAL_THEMES[mode];
            
            // Update particle energy with smooth transition
            this.particles.forEach(particle => {
                particle.energy = Math.random() * theme.energy + (1 - theme.energy) * 0.5;
                // Reset pulse phase for synchronized transitions
                if (theme.pulse) {
                    particle.pulsePhase = Math.random() * Math.PI * 2;
                }
            });
            
            // Morph formation if different
            if (theme.formation !== this.currentFormation) {
                this.morphToFormation(theme.formation);
            }
            
            console.log('✅ Cognitive state synchronized:', mode);
        }
    }

    /**
     * Maintain Cognitive Connection
     * 
     * Why: Ensures Clever maintains continuous cognitive presence and connection awareness
     * Where: Called periodically to maintain system coherence and prevent drift
     * How: Monitors particle coherence, adjusts formation strength, maintains cognitive flow
     * 
     * Connects to:
     *     - main.js: Should be called periodically to maintain system health
     *     - evolution_engine.py: Cognitive state should be logged for learning
     *     - persona.py: Mode changes should trigger cognitive adjustments
     */
    maintainCognitiveConnection() {
        // Check if particles are maintaining formation coherence
        let formationCoherence = 0;
        let totalEnergy = 0;
        
        this.particles.forEach(particle => {
            if (particle.isInFormation) {
                const dx = particle.targetX - particle.x;
                const dy = particle.targetY - particle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                formationCoherence += (distance < 50) ? 1 : 0;
            }
            totalEnergy += particle.energy;
        });
        
        const coherenceRatio = formationCoherence / this.particles.length;
        const avgEnergy = totalEnergy / this.particles.length;
        
        // Adjust formation strength if coherence is low
        if (coherenceRatio < 0.7) {
            this.particles.forEach(particle => {
                if (particle.isInFormation) {
                    particle.formationStrength = Math.min(0.3, particle.formationStrength + 0.01);
                }
            });
        }
        
        // Boost energy if system is getting sluggish
        if (avgEnergy < 0.3) {
            this.particles.forEach(particle => {
                particle.energy = Math.max(particle.energy, 0.4);
            });
        }
        
        // Log cognitive health
        const cognitiveHealth = {
            coherence: coherenceRatio,
            energy: avgEnergy,
            mode: this.currentMode,
            formation: this.currentFormation,
            timestamp: Date.now()
        };
        
        // Expose to window for external monitoring
        window.cleverCognitiveStatus = cognitiveHealth;
        
        return cognitiveHealth;
    }
    
    morphToFormation(formationType) {
        console.log('Morphing to formation:', formationType);
        this.currentFormation = formationType;
        
        switch (formationType) {
            case 'sphere':
                this.createSphereFormation();
                break;
            case 'rotating_sphere':
                this.createRotatingSphereFormation();
                break;
            case 'helix':
                this.createHelixFormation();
                break;
            case 'constellation':
                this.createConstellationFormation();
                break;
            default:
                this.releaseFormation();
        }
    }
    
    createSphereFormation() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = Math.min(this.canvas.width, this.canvas.height) * 0.2;
        
        this.particles.forEach((particle, index) => {
            const phi = Math.acos(1 - 2 * (index + 0.5) / this.particles.length);
            const theta = Math.PI * (1 + Math.sqrt(5)) * (index + 0.5);
            
            particle.targetX = centerX + radius * Math.sin(phi) * Math.cos(theta);
            particle.targetY = centerY + radius * Math.sin(phi) * Math.sin(theta);
            particle.isInFormation = true;
            particle.formationStrength = 0.15;
        });
    }

    /**
     * Create Rotating Sphere Formation for Idle State
     * 
     * Why: Provides continuous gentle rotation representing Clever's cognitive background processing
     * Where: Used by idle and observing modes for continuous visual engagement
     * How: Fibonacci sphere distribution with rotation parameters for smooth orbital motion
     * 
     * Connects to:
     *     - setMode(): Called when switching to idle or observing modes
     *     - Particle.update(): Particles use rotation properties for continuous movement
     *     - VISUAL_THEMES: Uses rotation settings from theme configuration
     */
    createRotatingSphereFormation() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = Math.min(this.canvas.width, this.canvas.height) * 0.25;
        
        this.particles.forEach((particle, index) => {
            // Clear mathematical shape properties for rotating sphere
            particle.mathematicalPoint = false;
            
            // Fibonacci sphere distribution for optimal coverage
            const phi = Math.acos(1 - 2 * (index + 0.5) / this.particles.length);
            const theta = Math.PI * (1 + Math.sqrt(5)) * (index + 0.5);
            
            // Base sphere position
            particle.baseX = centerX;
            particle.baseY = centerY;
            particle.rotationRadius = radius * Math.sin(phi);
            particle.targetX = centerX + particle.rotationRadius * Math.cos(theta);
            particle.targetY = centerY + particle.rotationRadius * Math.sin(theta);
            
            // Set rotation properties for continuous movement
            particle.rotationAngle = theta;
            particle.rotationSpeed = (0.005 + Math.random() * 0.01) * (Math.random() > 0.5 ? 1 : -1);
            
            particle.isInFormation = true;
            particle.formationStrength = 0.12;
        });
        
        console.log('🌀 Rotating sphere formation created for continuous cognitive visualization');
    }
    
    /**
     * Create Perfect 3D Mathematical Shape Formation
     * 
     * Why: Creates geometrically perfect 3D shapes using particles at vertices for
     *      stunning visual demonstrations of mathematical precision
     * Where: Called when shape_data is provided in context from persona responses
     * How: Places particles at calculated 3D vertices with proper perspective
     * 
     * Connects to:
     *     - shape_generator.py: Receives shape type and properties
     *     - persona.py: Called when shape commands generate shape_data in context
     *     - Particle.update(): Particles animate to 3D vertex positions
     */
    createMathematicalShape(shapeData) {
        if (!shapeData || !shapeData.properties) {
            console.warn('Invalid shape data provided to createMathematicalShape');
            return this.createSphereFormation(); // Fallback
        }

        const canvasWidth = this.canvas.width;
        const canvasHeight = this.canvas.height;
        const centerX = canvasWidth / 2;
        const centerY = canvasHeight / 2;

        // Detect shape type and create perfect 3D geometry
        const shapeName = shapeData.name.toLowerCase();
        const properties = shapeData.properties;
        
        console.log(`📐 Creating perfect 3D ${shapeName} with vertices`);

        let vertices = [];
        let radius = Math.min(canvasWidth, canvasHeight) * 0.25; // Size for visibility
        
        // Special scaling for DNA structures - make them much more prominent
        if (shapeName.includes('dna') || shapeName.includes('double helix') || shapeName.includes('genetic')) {
            radius = Math.min(canvasWidth, canvasHeight) * 0.4; // Larger base size for DNA
        }

        if (shapeName.includes('hexagon') || (properties.sides && properties.sides === 6)) {
            // Perfect 3D hexagon vertices
            vertices = this.createHexagonVertices(centerX, centerY, radius);
        } else if (shapeName.includes('triangle') || (properties.sides && properties.sides === 3)) {
            // Perfect 3D triangle vertices
            vertices = this.createTriangleVertices(centerX, centerY, radius);
        } else if (shapeName.includes('pentagon') || (properties.sides && properties.sides === 5)) {
            // Perfect 3D pentagon vertices
            vertices = this.createPentagonVertices(centerX, centerY, radius);
        } else if (shapeName.includes('square') || (properties.sides && properties.sides === 4)) {
            // Perfect 3D square vertices
            vertices = this.createSquareVertices(centerX, centerY, radius);
        } else if (shapeName.includes('cube') || shapeName.includes('box')) {
            // Perfect 3D cube wireframe vertices
            vertices = this.createCubeVertices(centerX, centerY, radius);
        } else if (shapeName.includes('pyramid') || shapeName.includes('tetrahedron')) {
            // Perfect 3D pyramid wireframe vertices  
            vertices = this.createPyramidVertices(centerX, centerY, radius);
        } else if (shapeName.includes('cone')) {
            // Perfect 3D cone wireframe vertices
            vertices = this.createConeVertices(centerX, centerY, radius);
        } else if (shapeName.includes('cylinder') || shapeName.includes('tube')) {
            // Perfect 3D cylinder wireframe vertices
            vertices = this.createCylinderVertices(centerX, centerY, radius);
        } else if (shapeName.includes('sphere_3d') || shapeName.includes('ball')) {
            // Perfect 3D sphere wireframe vertices
            vertices = this.create3DSphereVertices(centerX, centerY, radius);
        } else if (shapeName.includes('circle') || shapeName.includes('sphere')) {
            // Perfect circle vertices
            vertices = this.createCircleVertices(centerX, centerY, radius);
        } else if (shapeName.includes('dna') || shapeName.includes('double helix') || shapeName.includes('genetic')) {
            // DNA double helix vertices - CHECK BEFORE general helix to avoid conflicts
            vertices = this.createDNAVertices(centerX, centerY, radius, properties);
        } else if (shapeName.includes('spiral') || shapeName.includes('helix')) {
            // Spiral/helix vertices
            vertices = this.createSpiralVertices(centerX, centerY, radius, properties);
        } else if (shapeName.includes('fractal') || shapeName.includes('snowflake') || shapeName.includes('koch')) {
            // Fractal vertices
            vertices = this.createFractalVertices(centerX, centerY, radius, properties);
        } else if (shapeName.includes('star') || (properties.star_points)) {
            // Star polygon vertices
            vertices = this.createStarVertices(centerX, centerY, radius, properties.star_points || 5);
        } else if (shapeName.includes('polygon') && properties.sides) {
            // Specific sided polygon
            vertices = this.createPolygonVertices(centerX, centerY, radius, properties.sides);
        } else {
            // Generic polygon or fallback to hexagon for unknown shapes
            const sides = properties.sides || 6;
            vertices = this.createPolygonVertices(centerX, centerY, radius, sides);
        }

        // Clear all particles from previous formations
        this.particles.forEach(particle => {
              particle.isInFormation = false;
              particle.mathematicalPoint = false;
                particle.mathematicalPoint = false;
        });

        // Assign particles to vertices (one particle per vertex + extra distributed)
        const vertexCount = vertices.length;
        const particlesPerVertex = Math.floor(this.particles.length / vertexCount);
        const extraParticles = this.particles.length % vertexCount;

        let particleIndex = 0;

        // Place primary particles at vertices
        vertices.forEach((vertex, i) => {
            for (let j = 0; j < particlesPerVertex; j++) {
                if (particleIndex < this.particles.length) {
                    const particle = this.particles[particleIndex];
                    
                    // Add slight random offset for visual depth
                    const offsetRadius = j * 8; // Spread particles around vertex
                    const offsetAngle = (j / particlesPerVertex) * Math.PI * 2;
                    
                    particle.targetX = vertex.x + Math.cos(offsetAngle) * offsetRadius;
                    particle.targetY = vertex.y + Math.sin(offsetAngle) * offsetRadius;
                    particle.isInFormation = true;
                    particle.formationStrength = 0.3;
                    
                    // Mark as mathematical vertex
                    particle.mathematicalPoint = {
                        vertexIndex: i,
                        originalX: vertex.x,
                        originalY: vertex.y,
                        originalZ: vertex.z || 0,
                        shapeName: shapeData.name,
                        isVertex: true
                    };
                    
                    particleIndex++;
                }
            }
        });

        // Distribute remaining particles
        for (let i = 0; i < extraParticles; i++) {
            if (particleIndex < this.particles.length) {
                const particle = this.particles[particleIndex];
                const vertex = vertices[i % vertexCount];
                
                particle.targetX = vertex.x + (Math.random() - 0.5) * 30;
                particle.targetY = vertex.y + (Math.random() - 0.5) * 30;
                particle.isInFormation = true;
                particle.formationStrength = 0.2;
                
                particle.mathematicalPoint = {
                    vertexIndex: i % vertexCount,
                    originalX: vertex.x,
                    originalY: vertex.y,
                    originalZ: vertex.z || 0,
                    shapeName: shapeData.name,
                    isVertex: false
                };
                
                particleIndex++;
            }
        }

        console.log(`✨ Perfect 3D ${shapeName} created with ${vertexCount} vertices using ${particleIndex} particles`);
        
        // Store shape metadata
        this.currentShapeData = {
            ...shapeData,
            vertices: vertices,
            vertexCount: vertexCount
        };
    }

    /**
     * Create shape from API-provided data (adapter)
     * 
     * Why: Normalize /api/generate_shape response into engine renderer
     * Where: Called by main.js when shape commands are detected
     * How: Accepts result.shape or compatible object and forwards to mathematical creator
     */
    createShapeFromData(payload) {
        try {
            const shape = payload?.shape || payload;
            if (!shape) {
                console.warn('createShapeFromData: invalid payload', payload);
                return;
            }
            // Attempt to build a minimal shapeData compatible with createMathematicalShape
            const name = shape.name || shape.type || 'shape';
            const properties = shape.properties || shape.data?.properties || {};
            const points = (shape.points) || (shape.data?.vertices?.map(v => ({ x: v[0], y: v[1], z: v[2] || 0 })) ?? []);
            this.createMathematicalShape({ name, properties, points });
        } catch (e) {
            console.error('createShapeFromData error:', e);
        }
    }

    createHexagonVertices(centerX, centerY, radius) {
        const vertices = [];
        for (let i = 0; i < 6; i++) {
            const angle = (i * Math.PI) / 3; // 60 degrees apart
            vertices.push({
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius,
                z: 0
            });
        }
        return vertices;
    }

    createTriangleVertices(centerX, centerY, radius) {
        const vertices = [];
        for (let i = 0; i < 3; i++) {
            const angle = (i * 2 * Math.PI) / 3 - Math.PI / 2; // Start at top
            vertices.push({
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius,
                z: 0
            });
        }
        return vertices;
    }

    createPentagonVertices(centerX, centerY, radius) {
        const vertices = [];
        for (let i = 0; i < 5; i++) {
            const angle = (i * 2 * Math.PI) / 5 - Math.PI / 2;
            vertices.push({
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius,
                z: 0
            });
        }
        return vertices;
    }

    createSquareVertices(centerX, centerY, radius) {
        const vertices = [];
        for (let i = 0; i < 4; i++) {
            const angle = (i * Math.PI) / 2 + Math.PI / 4; // 45° offset for diamond orientation
            vertices.push({
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius,
                z: 0
            });
        }
        return vertices;
    }

    createPolygonVertices(centerX, centerY, radius, sides) {
        const vertices = [];
        for (let i = 0; i < sides; i++) {
            const angle = (i * 2 * Math.PI) / sides - Math.PI / 2;
            vertices.push({
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius,
                z: 0
            });
        }
        return vertices;
    }

    createCubeVertices(centerX, centerY, radius) {
        // Create 3D cube vertices with perspective projection
        const vertices = [];
        const size = radius * 0.8; // Scale for better visibility
        const perspectiveFactor = 300;
        
        // 8 vertices of cube in 3D space - Y is vertical axis
        const cubeVertices3D = [
            // Bottom face (y = -size/2)
            [-size/2, -size/2, -size/2],  // 0: back-left-bottom
            [ size/2, -size/2, -size/2],  // 1: back-right-bottom  
            [ size/2, -size/2,  size/2],  // 2: front-right-bottom
            [-size/2, -size/2,  size/2],  // 3: front-left-bottom
            // Top face (y = size/2)
            [-size/2,  size/2, -size/2],  // 4: back-left-top
            [ size/2,  size/2, -size/2],  // 5: back-right-top
            [ size/2,  size/2,  size/2],  // 6: front-right-top
            [-size/2,  size/2,  size/2],  // 7: front-left-top
        ];
        
        // Project 3D vertices to 2D with perspective
        cubeVertices3D.forEach(([x, y, z]) => {
            const projectedX = (x * perspectiveFactor) / (perspectiveFactor + z);
            const projectedY = (y * perspectiveFactor) / (perspectiveFactor + z);
            
            vertices.push({
                x: centerX + projectedX,
                y: centerY + projectedY,
                z: z
            });
        });
        
        return vertices;
    }

    createPyramidVertices(centerX, centerY, radius) {
        // Create 3D pyramid (tetrahedron) vertices with perspective projection
        const vertices = [];
        const size = radius * 0.8;
        const height = size * Math.sqrt(2/3); // Proper tetrahedron height
        const perspectiveFactor = 300;
        
        // 4 vertices of tetrahedron in 3D space - Y is vertical axis
        const pyramidVertices3D = [
            // Base triangle vertices (at y = -height/3)
            [-size/2, -height/3, -size/(2*Math.sqrt(3))], // Base vertex 1
            [ size/2, -height/3, -size/(2*Math.sqrt(3))], // Base vertex 2
            [0, -height/3, size/Math.sqrt(3)],            // Base vertex 3
            // Apex
            [0, height*2/3, 0]                            // Apex vertex (top)
        ];
        
        // Project 3D vertices to 2D with perspective
        pyramidVertices3D.forEach(([x, y, z]) => {
            const projectedX = (x * perspectiveFactor) / (perspectiveFactor + z);
            const projectedY = (y * perspectiveFactor) / (perspectiveFactor + z);
            
            vertices.push({
                x: centerX + projectedX,
                y: centerY + projectedY,
                z: z
            });
        });
        
        return vertices;
    }

    createConeVertices(centerX, centerY, radius) {
        /**
         * Create 3D Cone Wireframe Vertices with Perspective Projection
         * 
         * Why: Generates mathematical cone with circular base and apex for 3D visualization
         * Where: Called when cone shapes are detected in shape generation
         * How: Creates circular base vertices and apex, applies perspective projection
         */
        const vertices = [];
        const size = radius * 0.8;
        const height = size * 0.8;
        const baseRadius = size / 2;
        const numBasePoints = 12; // Circular base resolution
        const perspectiveFactor = 300;
        
        // Generate circular base vertices in 3D (at y = -height/2)
        for (let i = 0; i < numBasePoints; i++) {
            const angle = (2 * Math.PI * i) / numBasePoints;
            const x = baseRadius * Math.cos(angle);
            const z = baseRadius * Math.sin(angle);
            const y = -height / 2;
            
            // Apply perspective projection
            const projectedX = (x * perspectiveFactor) / (perspectiveFactor + z);
            const projectedY = (y * perspectiveFactor) / (perspectiveFactor + z);
            
            vertices.push({
                x: centerX + projectedX,
                y: centerY + projectedY,
                z: z
            });
        }
        
        // Add apex vertex (at y = height/2)
        const apexY = height / 2;
        vertices.push({
            x: centerX,
            y: centerY + apexY,
            z: 0
        });
        
        return vertices;
    }

    createCylinderVertices(centerX, centerY, radius) {
        /**
         * Create 3D Cylinder Wireframe Vertices with Perspective Projection
         * 
         * Why: Generates mathematical cylinder with top and bottom circles for 3D visualization
         * Where: Called when cylinder/tube shapes are detected in shape generation
         * How: Creates two circular ends connected by vertical lines, applies perspective
         */
        const vertices = [];
        const size = radius * 0.8;
        const height = size * 0.8;
        const cylRadius = size * 0.6;
        const numCirclePoints = 10; // Circle resolution
        const perspectiveFactor = 300;
        
        // Generate bottom circle vertices (at y = -height/2)
        for (let i = 0; i < numCirclePoints; i++) {
            const angle = (2 * Math.PI * i) / numCirclePoints;
            const x = cylRadius * Math.cos(angle);
            const z = cylRadius * Math.sin(angle);
            const y = -height / 2;
            
            const projectedX = (x * perspectiveFactor) / (perspectiveFactor + z);
            const projectedY = (y * perspectiveFactor) / (perspectiveFactor + z);
            
            vertices.push({
                x: centerX + projectedX,
                y: centerY + projectedY,
                z: z
            });
        }
        
        // Generate top circle vertices (at y = height/2)
        for (let i = 0; i < numCirclePoints; i++) {
            const angle = (2 * Math.PI * i) / numCirclePoints;
            const x = cylRadius * Math.cos(angle);
            const z = cylRadius * Math.sin(angle);
            const y = height / 2;
            
            const projectedX = (x * perspectiveFactor) / (perspectiveFactor + z);
            const projectedY = (y * perspectiveFactor) / (perspectiveFactor + z);
            
            vertices.push({
                x: centerX + projectedX,
                y: centerY + projectedY,
                z: z
            });
        }
        
        return vertices;
    }

    create3DSphereVertices(centerX, centerY, radius) {
        /**
         * Create 3D Sphere Wireframe Vertices with Latitude/Longitude Lines
         * 
         * Why: Generates true 3D sphere wireframe using spherical coordinates for realistic visualization
         * Where: Called when 3D sphere shapes are detected in shape generation
         * How: Uses spherical coordinates (theta, phi) to create latitude/longitude grid
         */
        const vertices = [];
        const sphereRadius = radius * 0.7;
        const latSegments = 6; // Latitude lines
        const lonSegments = 8; // Longitude lines
        const perspectiveFactor = 300;
        
        // Generate sphere vertices using spherical coordinates
        for (let lat = 0; lat <= latSegments; lat++) {
            const theta = (lat / latSegments) * Math.PI; // 0 to π (latitude)
            
            for (let lon = 0; lon < lonSegments; lon++) {
                const phi = (lon / lonSegments) * 2 * Math.PI; // 0 to 2π (longitude)
                
                // Convert spherical to cartesian coordinates - Y is vertical
                const x = sphereRadius * Math.sin(theta) * Math.cos(phi);
                const y = sphereRadius * Math.cos(theta);
                const z = sphereRadius * Math.sin(theta) * Math.sin(phi);
                
                // Apply perspective projection
                const projectedX = (x * perspectiveFactor) / (perspectiveFactor + z);
                const projectedY = (y * perspectiveFactor) / (perspectiveFactor + z);
                
                vertices.push({
                    x: centerX + projectedX,
                    y: centerY + projectedY,
                    z: z
                });
            }
        }
        
        return vertices;
    }

    createStarVertices(centerX, centerY, radius, starPoints = 5) {
        /**
         * Create Star Polygon Vertices
         * 
         * Why: Generates beautiful star shapes with alternating outer and inner points
         * Where: Called when star shapes are detected in shape generation
         * How: Creates alternating outer/inner vertices using trigonometry
         */
        const vertices = [];
        const outerRadius = radius;
        const innerRadius = radius * 0.4; // Inner points at 40% of outer radius
        const vertexCount = starPoints * 2; // Each star point creates 2 vertices
        
        for (let i = 0; i < vertexCount; i++) {
            const angle = (2 * Math.PI * i) / vertexCount - Math.PI / 2; // Start at top
            
            // Alternate between outer and inner radius
            const currentRadius = (i % 2 === 0) ? outerRadius : innerRadius;
            
            vertices.push({
                x: centerX + Math.cos(angle) * currentRadius,
                y: centerY + Math.sin(angle) * currentRadius,
                z: 0
            });
        }
        
        return vertices;
    }

    createCircleVertices(centerX, centerY, radius) {
        // Create vertices around a circle for sphere representation
        const vertices = [];
        const numPoints = 12; // Circle points for smooth sphere
        
        for (let i = 0; i < numPoints; i++) {
            const angle = (i * 2 * Math.PI) / numPoints;
            vertices.push({
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius,
                z: 0
            });
        }
        return vertices;
    }

    createSpiralVertices(centerX, centerY, radius, properties) {
        // Create 3D helix spiral vertices with depth and perspective projection
        const vertices = [];
        const turns = properties.turns || 3;
        const numPoints = properties.point_count || 60;
        const spiralType = properties.spiral_type || 'archimedean';
        const helixHeight = radius * 0.8; // Total height of the helix
        const perspectiveFactor = 300; // Perspective projection strength
        
        for (let i = 0; i < numPoints; i++) {
            const t = (i / numPoints) * turns * 2 * Math.PI;
            const progress = i / numPoints; // 0 to 1 progression along spiral
            let r, angle;
            
            if (spiralType === 'fibonacci') {
                // Fibonacci spiral (golden ratio)
                const phi = (1 + Math.sqrt(5)) / 2; // Golden ratio
                r = Math.sqrt(i) * (radius / Math.sqrt(numPoints)) * phi;
                angle = i * (137.508 * Math.PI / 180); // Golden angle in radians
            } else {
                // Archimedean spiral (constant spacing)
                r = progress * radius;
                angle = t;
            }
            
            // Create 3D helix coordinates - Y is vertical, X/Z horizontal
            const x3d = r * Math.cos(angle);  // X is horizontal circular motion
            const y3d = (progress - 0.5) * helixHeight;  // Y is vertical axis (screen vertical)
            const z3d = r * Math.sin(angle);  // Z is horizontal circular motion (depth)
            
            // Apply perspective projection for 3D depth effect
            const projectedX = (x3d * perspectiveFactor) / (perspectiveFactor + z3d);
            const projectedY = (y3d * perspectiveFactor) / (perspectiveFactor + z3d);
            
            vertices.push({
                x: centerX + projectedX,
                y: centerY + projectedY,
                z: z3d // Keep original z for rotation calculations
            });
        }
        return vertices;
    }

    createFractalVertices(centerX, centerY, radius, properties) {
        // Create 3D fractal vertices (Koch snowflake with depth variation)
        const vertices = [];
        const iterations = properties.iterations || 3;
        const baseSize = radius * 0.8;
        const maxDepth = radius * 0.3; // Maximum Z variation for 3D effect
        const perspectiveFactor = 300;
        
        // Start with triangle base
        const startTriangle = [
            { x: -baseSize, y: baseSize/2, z: 0 },
            { x: baseSize, y: baseSize/2, z: 0 },
            { x: 0, y: -baseSize * Math.sqrt(3)/2, z: 0 }
        ];
        
        // For simplicity, approximate fractal with many small segments
        const segments = Math.pow(4, iterations); // Each iteration quadruples segments
        
        startTriangle.forEach((vertex, vertexIndex) => {
            const nextVertex = startTriangle[(vertexIndex + 1) % 3];
            
            // Create fractal-like segments between vertices
            for (let i = 0; i <= segments/3; i++) {
                const t = i / (segments/3);
                const baseX = vertex.x + t * (nextVertex.x - vertex.x);
                const baseY = vertex.y + t * (nextVertex.y - vertex.y);
                
                // Add fractal-like noise/bumps with 3D depth
                const noiseAmplitude = baseSize * 0.1 / (iterations + 1);
                const noiseX = (Math.random() - 0.5) * noiseAmplitude;
                const noiseY = (Math.random() - 0.5) * noiseAmplitude;
                const noiseZ = (Math.random() - 0.5) * maxDepth; // Add Z variation
                
                // Apply perspective projection for 3D effect
                const x3d = baseX + noiseX;
                const y3d = baseY + noiseY;
                const z3d = noiseZ;
                
                const projectedX = (x3d * perspectiveFactor) / (perspectiveFactor + z3d);
                const projectedY = (y3d * perspectiveFactor) / (perspectiveFactor + z3d);
                
                vertices.push({
                    x: centerX + projectedX,
                    y: centerY + projectedY,
                    z: z3d
                });
            }
        });
        
        return vertices;
    }

    createDNAVertices(centerX, centerY, radius, properties) {
        // Create DNA double helix vertices with 3D perspective
        const vertices = [];
        const turns = properties.turns || 2.5;
        const numPoints = properties.point_count || 80;
        // Height should be proportional to screen, not radius, to keep DNA centered and visible
        const helixHeight = Math.min(this.canvas.height * 0.6, radius * 2.5); // Keep DNA within 60% of screen height
        const helixRadius = radius * 1.2; // Much larger radius for prominent DNA structure
        const perspectiveFactor = 300;
        
        for (let i = 0; i < numPoints; i++) {
            const t = (i / numPoints) * turns * 2 * Math.PI;
            const progress = i / numPoints; // 0 to 1 progression along helix
            
            // Vertical position along the helix
            const yPos = (progress - 0.5) * helixHeight;
            
            // First helix strand (backbone 1)
            const x1_3d = helixRadius * Math.cos(t);
            const z1_3d = helixRadius * Math.sin(t);
            
            // Second helix strand (backbone 2) - 180° phase shift
            const x2_3d = helixRadius * Math.cos(t + Math.PI);
            const z2_3d = helixRadius * Math.sin(t + Math.PI);
            
            // Apply perspective projection for 3D effect
            const x1_proj = (x1_3d * perspectiveFactor) / (perspectiveFactor + z1_3d);
            const x2_proj = (x2_3d * perspectiveFactor) / (perspectiveFactor + z2_3d);
            
            // Add backbone vertices
            vertices.push(
                {
                    x: centerX + x1_proj,
                    y: centerY + yPos,
                    z: z1_3d,
                    strand: 'backbone1'
                },
                {
                    x: centerX + x2_proj,
                    y: centerY + yPos,
                    z: z2_3d,
                    strand: 'backbone2'
                }
            );
            
            // Add base pairs (connecting rungs) every 6th point
            if (i % 6 === 0) {
                const baseSteps = 4; // Points between strands for base pair
                for (let step = 1; step < baseSteps; step++) {
                    const stepRatio = step / baseSteps;
                    
                    // Interpolate between the two strands
                    const base_x3d = x1_3d + stepRatio * (x2_3d - x1_3d);
                    const base_z3d = z1_3d + stepRatio * (z2_3d - z1_3d);
                    const base_x_proj = (base_x3d * perspectiveFactor) / (perspectiveFactor + base_z3d);
                    
                    vertices.push({
                        x: centerX + base_x_proj,
                        y: centerY + yPos,
                        z: base_z3d,
                        strand: 'base_pair'
                    });
                }
            }
        }
        
        return vertices;
    }

    createHelixFormation() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = Math.min(this.canvas.width, this.canvas.height) * 0.15;
        const height = Math.min(this.canvas.width, this.canvas.height) * 0.3;
        
        this.particles.forEach((particle, index) => {
            const t = (index / this.particles.length) * Math.PI * 4;
            const y_offset = (index / this.particles.length) * height - height / 2;
            
            particle.targetX = centerX + radius * Math.cos(t);
            particle.targetY = centerY + y_offset + radius * 0.2 * Math.sin(t * 2);
            particle.isInFormation = true;
            particle.formationStrength = 0.12;
        });
    }
    
    createConstellationFormation() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const clusters = 5;
        
        this.particles.forEach((particle, index) => {
            const clusterIndex = Math.floor(index / (this.particles.length / clusters));
            const clusterAngle = (clusterIndex / clusters) * Math.PI * 2;
            const clusterRadius = Math.min(this.canvas.width, this.canvas.height) * 0.25;
            
            const clusterX = centerX + Math.cos(clusterAngle) * clusterRadius;
            const clusterY = centerY + Math.sin(clusterAngle) * clusterRadius;
            
            const spread = 50;
            particle.targetX = clusterX + (Math.random() - 0.5) * spread;
            particle.targetY = clusterY + (Math.random() - 0.5) * spread;
            particle.isInFormation = true;
            particle.formationStrength = 0.08;
        });
    }
    
    releaseFormation() {
        this.particles.forEach(particle => {
            particle.isInFormation = false;
            particle.formationStrength = 0;
            
            // Clear mathematical shape properties to restore idle rotation
            particle.mathematicalPoint = false;
            
            // Reset rotation properties for idle state
            particle.rotationSpeed = (Math.random() - 0.5) * 0.02;
            particle.rotationRadius = Math.random() * 20;
        });
        console.log('🌀 Formation released, particles restored to idle rotation');
    }
    
    /**
     * Render Connection Lines Between Nearby Particles
     * 
     * Why: Creates visible neural network connections that make formations more clear
     * Where: Called during animation loop before particle rendering
     * How: Draws lines between particles within connection distance with opacity based on proximity
     * 
     * Connects to:
     *     - animate(): Called during each animation frame
     *     - Particle.distanceTo(): Uses particle distance calculation
     *     - VISUAL_THEMES: Uses current mode colors for connection styling
     */
    renderConnections() {
        const connectionDistance = 120; // Maximum distance for connections
        const maxOpacity = 0.6;
        const theme = VISUAL_THEMES[this.currentMode] || VISUAL_THEMES.idle;
        
        this.ctx.save();
        
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const particle1 = this.particles[i];
                const particle2 = this.particles[j];
                const distance = particle1.distanceTo(particle2);
                
                if (distance < connectionDistance) {
                    // Calculate connection opacity based on distance
                    const opacity = maxOpacity * (1 - distance / connectionDistance);
                    
                    // Use theme color for connections
                    const connectionColor = theme.colors[0]; // Primary theme color
                    
                    this.ctx.strokeStyle = connectionColor;
                    this.ctx.globalAlpha = opacity * 0.4; // Subtle connections
                    this.ctx.lineWidth = 1;
                    
                    this.ctx.beginPath();
                    this.ctx.moveTo(particle1.x, particle1.y);
                    this.ctx.lineTo(particle2.x, particle2.y);
                    this.ctx.stroke();
                }
            }
        }
        
        this.ctx.restore();
    }
    
    animate() {
        if (this.isAnimating) return;
        
        this.isAnimating = true;
        let frameCount = 0;
        
        const animateFrame = () => {
            frameCount++;
            // FPS tracking (EMA)
            const now = performance.now();
            const dt = Math.max(1, now - this._lastFrameTs);
            const instFps = 1000 / dt;
            this._fpsEMA = this._fpsEMA * 0.9 + instFps * 0.1;
            this._lastFrameTs = now;
            
            // Clear canvas with subtle fade for smoother trails
            this.ctx.fillStyle = '#0B0F14';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            
            // Add cognitive background grid for depth
            this.renderCognitiveGrid(frameCount);
            
            // Update particles
            this.particles.forEach(particle => {
                particle.update();
            });
            
            // Update particle-based UI elements
            this.updateParticleUI();
            
            // Render connection lines between nearby particles
            this.renderConnections();

            // Render intelligent conversation links between particle-formed chat panels
            this.renderChatFlowConnections();
            
            // Render particles
            this.particles.forEach(particle => {
                particle.render(this.ctx);
            });
            
            // Render particle-formed UI elements on top
            this.renderParticleUI();
            
            // Add central cognitive pulse for idle state
            if (this.currentMode === 'idle' || this.currentMode === 'observing') {
                this.renderCognitiveCore(frameCount);
            }
            
            this.animationId = requestAnimationFrame(animateFrame);
        };
        
        animateFrame();
        console.log('🧠 Cognitive animation started with enhanced visualization');
    }

    /** Toggle diagnostics overlay */
    setDiagnosticsEnabled(enabled) {
        this._diagnosticsEnabled = !!enabled;
    }

    renderDiagnosticsOverlay() {
        try {
            this.ctx.save();
            this.ctx.globalAlpha = 0.9;
            this.ctx.fillStyle = 'rgba(10,16,22,0.8)';
            this.ctx.strokeStyle = 'rgba(125, 211, 252, 0.8)';
            const pad = 8;
            const w = 260, h = 78;
            this.ctx.fillRect(10, 10, w, h);
            this.ctx.strokeRect(10, 10, w, h);
            this.ctx.fillStyle = '#E2E8F0';
            this.ctx.font = '12px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto';
            const fps = Math.round(this._fpsEMA);
            const prof = this._lastPanelProfile || { speed: 0, amplitude: 0, jitter: 0 };
            const ctxLine1 = `FPS: ${fps}`;
            const ctxLine2 = `Pulse: speed=${prof.speed?.toFixed?.(3) ?? prof.speed}, amp=${prof.amplitude?.toFixed?.(2) ?? prof.amplitude}`;
            const ctxLine3 = `Domain: ${this._lastPanelContext.domain} | Mood: ${this._lastPanelContext.mood}`;
            this.ctx.fillText(ctxLine1, 18, 28);
            this.ctx.fillText(ctxLine2, 18, 46);
            this.ctx.fillText(ctxLine3, 18, 64);
            this.ctx.restore();
        } catch {}
    }

    /**
     * Render Cognitive Grid Background
     * 
     * Why: Provides subtle spatial reference and depth for cognitive visualization
     * Where: Called during animation loop to create immersive background
     * How: Animated grid with breathing effect synchronized to cognitive state
     */
    renderCognitiveGrid(frameCount) {
        const theme = VISUAL_THEMES[this.currentMode] || VISUAL_THEMES.idle;
        const breathe = Math.sin(frameCount * 0.01) * 0.1 + 0.9;
        
        this.ctx.save();
        this.ctx.globalAlpha = 0.05 * breathe;
        this.ctx.strokeStyle = theme.colors[0];
        this.ctx.lineWidth = 1;
        
        const gridSize = 50;
        for (let x = 0; x < this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        
        for (let y = 0; y < this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
        
        this.ctx.restore();
    }

    /**
     * Render Central Cognitive Core
     * 
     * Why: Visual representation of Clever's central processing during idle states
     * Where: Called during idle/observing animation loops for cognitive presence
     * How: Pulsing central glow with synchronized breathing pattern
     */
    renderCognitiveCore(frameCount) {
        const theme = VISUAL_THEMES[this.currentMode] || VISUAL_THEMES.idle;
        const pulse = Math.sin(frameCount * 0.02) * 0.3 + 0.7;
        
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const coreRadius = 15 * pulse;
        
        this.ctx.save();
        
        // Create radial gradient for core
        const gradient = this.ctx.createRadialGradient(
            centerX, centerY, 0,
            centerX, centerY, coreRadius * 3
        );
        gradient.addColorStop(0, theme.colors[0] + '40');
        gradient.addColorStop(0.5, theme.colors[1] + '20');
        gradient.addColorStop(1, theme.colors[2] + '00');
        
        // Draw cognitive core
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, coreRadius * 3, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Draw inner core
        this.ctx.fillStyle = theme.colors[0] + '60';
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, coreRadius, 0, Math.PI * 2);
        this.ctx.fill();
        
        this.ctx.restore();
    }
    
    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.isAnimating = false;
        console.log('Animation stopped');
    }
    
    /**
     * Compute next panel position to avoid overlap and maintain rhythm
     * 
     * Why: Prevent rectangular panels from stacking or crashing into each other
     * Where: Used by createParticleChatBubble to choose final rect location
     * How: Alternates vertical offset and side placement with core clearance
     */
    _getNextPanelPosition(sideLabel, panelWidth, panelHeight) {
        const canvas = this.canvas;
        if (!this._panelLayout) {
            this._panelLayout = { rowIndex: 0 };
        }

        const verticalSpacing = Math.max(panelHeight + 40, 160);
        const usableHeight = canvas.height - 160; // leave top/bottom breathing room
        const maxRows = Math.max(1, Math.floor(usableHeight / verticalSpacing));

        const row = this._panelLayout.rowIndex % maxRows;
        this._panelLayout.rowIndex += 1;

        const topPadding = Math.max(40, (canvas.height - (maxRows - 1) * verticalSpacing) / 2);
        const targetY = Math.min(
            canvas.height - panelHeight - 40,
            Math.max(40, topPadding + row * verticalSpacing)
        );

        const coreClearance = 150 + (panelWidth / 2) + 6;
        const targetX = sideLabel === 'left'
            ? Math.max(20, canvas.width / 2 - coreClearance)
            : Math.min(canvas.width - panelWidth - 20, canvas.width / 2 + coreClearance - panelWidth);

        return { x: Math.round(targetX), y: Math.round(targetY) };
    }
    
    /**
     * DYNAMIC UI CREATION: Create dynamic particle chat panel using recruited particles from Clever's body
     * 
     * Why: Chat panels emerge organically from Clever herself - particles flow from her body to form dynamic light cells
     * Where: Called when chat messages need to be displayed with enhanced visual feedback
     * How: Creates particle clusters that form rectangular/organic outlines with text rendering and domain-based animations
     */
    createParticleChatBubble(message, sender = 'ai', knowledgeDomain = null, mood = 'neutral') {
        // Theme via helper (explicit contract)
        const domain = knowledgeDomain || 'chat_interface';
        const moodName = mood || 'neutral';
        const dc = this.getDomainColor(domain, moodName);
        let bubbleColors = dc.colors;
        let energy = dc.glow;
        // Pulse intensity governed by profile + modulation
        let pulseIntensity = Math.min(0.7, 0.25 + energy * 0.5);
    // Gentle pulse speed scaling with message length (longer -> slightly slower)
    const len = Math.max(1, String(message || '').length);
    const speedScale = Math.max(0.85, Math.min(1.15, 1 - Math.max(0, (len - 140)) / 1200));

    // Adaptive dissolve speed: shorter messages dissolve quicker
    const baseDissolve = 0.02;
    const moodSlow = (mood === 'thoughtful' || mood === 'calm') ? 0.85 : 1.0;
    const dissolveSpeed = Math.max(0.012, Math.min(0.03, baseDissolve * (1.05 - Math.min(0.2, len / 1200)) * moodSlow));
        this.activeKnowledgeDomain = domain;

        // Size from text
        const bubbleMaxWidth = Math.min(520, this.canvas.width * 0.55);
        const linesForSize = this.wrapTextLinesForSize(message, bubbleMaxWidth - 32);
        const lineHeight = 18;
        const bubbleHeight = Math.max(72, linesForSize.count * lineHeight + 28);
        const bubbleWidth = Math.min(bubbleMaxWidth, Math.max(260, linesForSize.maxWidth + 32));

        // Centered spawn zone (≈300x200) around canvas center with left/right alternating columns
        const cx = this.canvas.width / 2;
        const cy = this.canvas.height / 2;
        this._panelParity = (this._panelParity || 0) + 1; // 1,2,3,...
        const side = (this._panelParity % 2 === 0) ? 1 : -1; // alternate right/left
        const spawnHalfW = 150; // ±150px horizontally
        const spawnHalfH = 100; // ±100px vertically

        // Horizontal column center offset; ensure 150px clearance from core + half panel
        const minClear = 150 + bubbleWidth / 2 + 6;
        let colOffset = Math.max(minClear, spawnHalfW - 10) * side; // bias to stay outside core
        // Small jitter within spawn zone
        const jitterX = (Math.random() - 0.5) * 30;
        const jitterY = (Math.random() - 0.5) * 30;

    // Use staggered positioning to avoid overlap
    const sideLabel = (side < 0) ? 'left' : 'right';
    const nextPos = this._getNextPanelPosition(sideLabel, bubbleWidth, bubbleHeight);
    const clampedX = nextPos.x;
    const clampedY = nextPos.y;

        const bubbleId = `particle-bubble-${Date.now()}`;

    // Create a modest number of particles along the rectangle perimeter to avoid overload
    // Previously 40–60; optimized to ~12–20 based on panel size for better performance
    const clusterSize = Math.max(12, Math.min(20, Math.round((bubbleWidth + bubbleHeight) * 0.05)));
        const particleCluster = this.createParticleCluster(cx, cy, clusterSize, bubbleColors);
        if (!particleCluster.length) {
            console.warn('🔮 No particles available for rectangular panel - Clever is busy');
            return null;
        }
        // Force initial spawn at center so formation visibly slides outward
        particleCluster.forEach(p => {
            // Preserve original positions for return
            if (p.originalX === undefined) { p.originalX = p.x; }
            if (p.originalY === undefined) { p.originalY = p.y; }
            p.x = cx; p.y = cy;
        });

        // Prepare cluster dynamics
        this.enhanceClusterForDynamicPanel(particleCluster, bubbleColors, energy, pulseIntensity);

    // Per-panel intensity modulation: longer text → stronger/longer brightness window
    const panelIntensityBoost = Math.min(1.4, 1.0 + Math.log2(1 + len / 140));
        const panelEnergy = Math.min(1.0, energy * panelIntensityBoost);

        // Register UI element (rectangular outline enforced)
        this.uiElements.set(bubbleId, {
            type: 'dynamic_chat_panel',
            particles: particleCluster,
            message,
            sender,
            knowledgeDomain: domain,
            mood: moodName,
            colors: bubbleColors,
            pulseProfile: dc.pulseProfile,
            x: clampedX,
            y: clampedY,
            width: bubbleWidth,
            height: bubbleHeight,
            alpha: 0,
            targetAlpha: 0.9,
            glowIntensity: 0,
            targetGlowIntensity: panelEnergy,
            pulsePhase: 0,
            pulseIntensity: pulseIntensity,
            pulseSpeedScale: speedScale,
            createdAt: Date.now(),
            phase: 'spawning',
            spawnTime: 250,
            formationTime: 700,
            glowTime: 400,
            displayTime: (typeof globalThis !== 'undefined' && /** @type {any} */ (globalThis).BUBBLE_VISIBLE_MS)
                ? /** @type {any} */ (globalThis).BUBBLE_VISIBLE_MS
                : 6000,
            // Adaptive linger: base 2.0s, longer if calm/thoughtful or longer text
            pulseTime: Math.round(1600 + Math.min(1400, len * 6) + (moodSlow < 1 ? 400 : 0)),
            dissolveTime: 900,
            dissolveSpeed: dissolveSpeed,
            outlineShape: 'rectangular',
            zIndex: 5 // behind transient effects, in front of background
        });

        // Track ordering for intelligent connection rendering
        this.chatBubbleOrder.push(bubbleId);

        // Update diagnostics context
        this._lastPanelProfile = dc.pulseProfile;
        this._lastPanelContext = { domain, mood: moodName };

        // Enforce a maximum number of simultaneously active panels for performance
        // If we exceed maxPanels, dissolve the oldest ones
        const maxPanels = 6;
        const activePanels = this.chatBubbleOrder.filter(id => {
            const el = this.uiElements.get(id);
            return el && el.type === 'dynamic_chat_panel';
        });
        if (activePanels.length > maxPanels) {
            const overflow = activePanels.length - maxPanels;
            for (let i = 0; i < overflow; i++) {
                const oldestId = activePanels[i];
                const oldestEl = this.uiElements.get(oldestId);
                if (oldestEl && oldestEl.phase !== 'dissolving') {
                    oldestEl.phase = 'dissolving';
                    console.log('💡 Auto-dissolving oldest panel to enforce cap:', oldestId);
                }
            }
        }

        console.log("🟦 Rectangular chat panel created:", { sender, position: { x: clampedX, y: clampedY, w: bubbleWidth, h: bubbleHeight } });
        return bubbleId;
    }

    /**
     * Clear or dissolve all active dynamic chat panels
     * 
     * Why: Allow UI and keyboard commands to clear conversation artifacts
     * Where: Invoked from main.js or global actions (e.g., clearChatMessages)
     * How: Either trigger dissolve phase for graceful exit or force remove
     */
    clearChatPanels(options = { graceful: true }) {
        const ids = [];
        this.uiElements.forEach((el, id) => {
            if (el.type === 'dynamic_chat_panel') ids.push(id);
        });
        if (!ids.length) return 0;
        const graceful = !!options.graceful;
        for (const id of ids) {
            const el = this.uiElements.get(id);
            if (!el) continue;
            if (graceful) {
                if (el.phase !== 'dissolving') el.phase = 'dissolving';
            } else {
                // Force release particles immediately
                if (el.particles) {
                    el.particles.forEach(particle => {
                        particle.isRecruited = false;
                        particle.dynamicPanel = false;
                        particle.color = particle.originalColor;
                        particle.size = particle.originalSize;
                        particle.isInFormation = false;
                    });
                }
                this.uiElements.delete(id);
            }
        }
        console.log(`💡 ${graceful ? 'Dissolving' : 'Cleared'} ${ids.length} chat panel(s)`);
        return ids.length;
    }

    /**
     * Compute visual center of a particle-formed chat bubble
     * 
     * Why: Connection lines should originate from the bubble's perceived center
     * Where: Used by renderChatFlowConnections() to connect message panels
     * How: Prefer average of recruited particle positions; fallback to rect center
     */
    getBubbleCenter(element) {
        if (!element) return { x: 0, y: 0 };
        if (element.particles && element.particles.length > 0) {
            let sx = 0, sy = 0;
            for (const p of element.particles) {
                sx += p.x;
                sy += p.y;
            }
            return { x: sx / element.particles.length, y: sy / element.particles.length };
        }
        return { x: element.x + element.width / 2, y: element.y + element.height / 2 };
    }

    /**
     * Render subtle connection lines between consecutive chat bubbles
     * 
     * Why: Visualize the thought flow across messages using Clever's own particles
     * Where: Called every frame during animate() before UI and particle rendering stack
     * How: Iterate chatBubbleOrder, draw bezier segments between bubble centers with knowledge-driven color
     */
    renderChatFlowConnections() {
        if (!this.chatBubbleOrder || this.chatBubbleOrder.length < 2) return;

        // Prune missing IDs while building an ordered list of active bubbles
        const active = [];
        for (const id of this.chatBubbleOrder) {
            if (this.uiElements.has(id)) active.push(id);
        }
        this.chatBubbleOrder = active; // keep clean

        if (this.chatBubbleOrder.length < 2) return;

        // Determine base stroke from current knowledge domain/theme
        const theme = (this.activeKnowledgeDomain && VISUAL_THEMES[this.activeKnowledgeDomain])
            ? VISUAL_THEMES[this.activeKnowledgeDomain]
            : VISUAL_THEMES.chat_interface;
        const stroke = theme.colors[0];

        this.ctx.save();
        this.ctx.lineWidth = 1.0;
        this.ctx.globalAlpha = 0.2; // subtle base beneath UI
        this.ctx.strokeStyle = stroke;

        for (let i = 0; i < this.chatBubbleOrder.length - 1; i++) {
            const a = this.uiElements.get(this.chatBubbleOrder[i]);
            const b = this.uiElements.get(this.chatBubbleOrder[i + 1]);
            if (!a || !b) continue;

            const ca = this.getBubbleCenter(a);
            const cb = this.getBubbleCenter(b);

            // Quadratic bezier with slight vertical arc for elegance
            const mx = (ca.x + cb.x) / 2;
            const my = (ca.y + cb.y) / 2 - 20; // lift control point for arc

            // Recency-weighted styling (newer = brighter/thicker)
            const now = Date.now();
            const age = Math.max(0, now - Math.max(a.createdAt || now, b.createdAt || now));
            const t = Math.max(0, 1 - Math.min(age / 30000, 1)); // 0..1 over 30s
            this.ctx.globalAlpha = 0.15 + 0.25 * t;
            this.ctx.lineWidth = 0.75 + 1.5 * t;

            this.ctx.beginPath();
            this.ctx.moveTo(ca.x, ca.y);
            this.ctx.quadraticCurveTo(mx, my, cb.x, cb.y);
            this.ctx.stroke();
        }

        this.ctx.restore();
    }

    /**
     * Create or reveal particle-formed input bar at bottom center
     */
    ensureInputBar() {
        if (this.inputBarId && this.uiElements.has(this.inputBarId)) return this.inputBarId;

        const barWidth = Math.min(520, this.canvas.width * 0.6);
        const barHeight = 44;
        const x = (this.canvas.width - barWidth) / 2;
        const y = this.canvas.height - barHeight - 24;
        const colors = VISUAL_THEMES.chat_interface.colors;

        const recruited = this.recruitParticlesForChatBubble(x, y, barWidth, barHeight, colors);
        if (!recruited.length) return null;

        this.enhanceParticleRecruitment(recruited);
        const id = `particle-input-${Date.now()}`;
        this.uiElements.set(id, {
            type: 'input_bar',
            particles: recruited,
            x, y, width: barWidth, height: barHeight,
            alpha: 0,
            targetAlpha: 0.95,
            createdAt: Date.now(),
            text: this.inputBarText || '',
            caretBlink: 0,
            focusGlow: this.inputBarFocus ? 1 : 0,
            targetFocusGlow: this.inputBarFocus ? 1 : 0,
            focused: this.inputBarFocus,
            phase: 'displaying'
        });
        this.inputBarId = id;
        return id;
    }

    setInputBarVisible(visible) {
        this.inputBarVisible = !!visible;
        if (this.inputBarVisible) {
            const id = this.ensureInputBar();
            if (id) {
                const element = this.uiElements.get(id);
                if (element) {
                    element.focused = this.inputBarFocus;
                    element.targetFocusGlow = this.inputBarFocus ? 1 : 0;
                    element.focusGlow = this.inputBarFocus ? 1 : 0;
                }
            }
        } else if (this.inputBarId) {
            this.inputBarFocus = false;
            this.inputBarFocusTarget = 0;
            const element = this.uiElements.get(this.inputBarId);
            if (element && element.particles) {
                element.particles.forEach(p => {
                    p.returning = true;
                    p.targetX = p.originalX;
                    p.targetY = p.originalY;
                    p.formationStrength = 0.05;
                });
            }
            this.uiElements.delete(this.inputBarId);
            this.inputBarId = null;
        }
    }

    updateInputBarText(text) {
        this.inputBarText = String(text ?? '');
        if (!this.inputBarId) return;
        const element = this.uiElements.get(this.inputBarId);
        if (element) {
            element.text = this.inputBarText;
            element.createdAt = Date.now();
        }
    }

    setInputBarFocusState(focused) {
        this.inputBarFocus = !!focused;
        this.inputBarFocusTarget = this.inputBarFocus ? 1 : 0;
        if (!this.inputBarId) return;
        const element = this.uiElements.get(this.inputBarId);
        if (element && element.type === 'input_bar') {
            element.focused = this.inputBarFocus;
            element.targetFocusGlow = this.inputBarFocusTarget;
            if (typeof element.focusGlow !== 'number') {
                element.focusGlow = this.inputBarFocusTarget;
            }
            element.targetAlpha = this.inputBarFocus ? 1.05 : 0.95;
        }
    }
    
    /**
     * Recruit particles from Clever's existing swarm for chat bubble formation
     * 
     * Why: Chat panels emerge from Clever herself - no artificial particle creation
     * Where: Called when creating chat bubbles to recruit existing particles
     * How: Finds 4 available particles and smoothly moves them to form square corners
     */
    recruitParticlesForChatBubble(x, y, width, height, colors) {
        const recruitedParticles = [];
        const availableParticles = this.particles.filter(p => !p.isRecruited && !p.isInFormation);
        
        // We need exactly 4 particles for the corners of the square panel
        if (availableParticles.length < 4) {
            console.warn('🔮 Not enough available particles for chat bubble - need 4, have', availableParticles.length);
            return [];
        }
        
        // Take the first 4 available particles
        const selectedParticles = availableParticles.slice(0, 4);
        
        // Calculate corner positions for square formation
        const corners = [
            { x: x, y: y }, // Top-left
            { x: x + width, y: y }, // Top-right  
            { x: x + width, y: y + height }, // Bottom-right
            { x: x, y: y + height } // Bottom-left
        ];
        
        selectedParticles.forEach((particle, index) => {
            // Store original properties for return journey
            particle.originalX = particle.x;
            particle.originalY = particle.y;
            particle.originalSize = particle.size;
            particle.originalColor = particle.color;
            
            // Mark as recruited and set formation targets
            particle.isRecruited = true;
            particle.recruitmentState = 'moving_to_formation'; // moving_to_formation -> in_formation -> returning_home
            particle.targetX = corners[index].x;
            particle.targetY = corners[index].y;
            particle.formationStrength = 0.15;
            particle.chatBubbleCorner = index;
            
            // Apply knowledge-driven color
            const colorIndex = Math.floor(Math.random() * colors.length);
            particle.color = colors[colorIndex];
            particle.size = 4 + Math.random() * 2; // Slightly larger for visibility
            
            recruitedParticles.push(particle);
        });
        
        console.log(`🔮 Recruited ${recruitedParticles.length} particles from Clever's body for chat panel`);
        return recruitedParticles;
    }
    
    /**
     * Enhanced particle recruitment with smooth recruitment animation
     * 
     * Why: Particles should visibly move from Clever's body to form chat interface
     * Where: Called during chat bubble formation to create organic flow
     * How: Smooth animation states tracking particle journey from body to interface
     */
    enhanceParticleRecruitment(recruitedParticles) {
        recruitedParticles.forEach(particle => {
            // Enhanced animation properties for smooth transitions
            particle.recruitmentPhase = 0; // 0-1 animation progress
            particle.recruitmentSpeed = 0.02 + Math.random() * 0.01; // Slight variation
            particle.pulsePhase = Math.random() * Math.PI * 2;
            particle.glowIntensity = 0;
            
            // Store journey waypoints for natural movement
            particle.journeyProgress = 0;
            particle.maxJourneyTime = 60; // frames to reach target
        });
    }
    
    /**
     * Create particle cluster for dynamic chat panels
     * 
     * Why: Generates enough particles to form organic or rectangular outlines for enhanced chat visualization
     * Where: Called by createParticleChatBubble for dynamic panel creation
     * How: Creates or recruits particles and positions them in a cluster formation near the text origin
     */
    createParticleCluster(centerX, centerY, clusterSize, colors) {
        const cluster = [];
        const availableParticles = this.particles.filter(p => !p.isRecruited && !p.isInFormation);
        
        // Recruit existing particles if available, otherwise create new ones
        for (let i = 0; i < clusterSize; i++) {
            let particle;
            
            if (i < availableParticles.length) {
                // Recruit existing particle
                particle = availableParticles[i];
                particle.isRecruited = true;
                particle.originalX = particle.x;
                particle.originalY = particle.y;
                particle.originalColor = particle.color || colors[0];
                particle.originalSize = particle.size;
            } else {
                // Create new particle if needed
                particle = new Particle(centerX, centerY, this);
                this.particles.push(particle);
                particle.isRecruited = true;
                particle.originalX = centerX;
                particle.originalY = centerY;
                particle.originalColor = colors[0];
                particle.originalSize = particle.size;
            }
            
            // Set cluster color based on domain
            particle.color = colors[i % colors.length];
            particle.clusterIndex = i;
            particle.clusterTotal = clusterSize;
            
            cluster.push(particle);
        }
        
        return cluster;
    }
    
    /**
     * Enhance particle cluster for dynamic panel formation
     * 
     * Why: Adds special properties for creating organic/rectangular outlines with glow and pulse effects
     * Where: Called after createParticleCluster to prepare particles for dynamic animation
     * How: Assigns formation targets, animation properties, and visual enhancement effects
     */
    enhanceClusterForDynamicPanel(cluster, colors, energy, pulseIntensity) {
        cluster.forEach((particle, index) => {
            // Enhanced visual properties
            particle.dynamicPanel = true;
            particle.energy = energy;
            particle.pulseIntensity = pulseIntensity;
            particle.pulsePhase = (index / cluster.length) * Math.PI * 2; // Staggered pulse
            particle.glowIntensity = 0;
            particle.targetGlowIntensity = energy;
            
            // Animation properties
            particle.formationPhase = 0; // 0-1 formation progress
            particle.formationSpeed = 0.015 + Math.random() * 0.01;
            particle.dissolvePhase = 0; // 0-1 dissolve progress
            
            // Size and visual enhancement
            particle.baseSize = particle.size;
            particle.targetSize = particle.size * (1.2 + energy * 0.3);
            particle.alpha = 0;
            particle.targetAlpha = 0.8 + energy * 0.2;
        });
    }
    
    /**
     * Update and render particle-based UI elements with recruitment lifecycle
     */
    updateParticleUI() {
        this.uiElements.forEach((element, id) => {
            if (element.type === 'chat_bubble') {
                const elapsed = Date.now() - element.createdAt;
                
                // Phase management: recruiting -> formed -> displaying -> returning
                if (element.phase === 'recruiting' && elapsed > element.formationTime) {
                    element.phase = 'formed';
                    console.log('🔮 Chat panel formed from Clever\'s particles');
                } else if (element.phase === 'formed' && elapsed > element.formationTime + 500) {
                    element.phase = 'displaying';
                } else if (element.phase === 'displaying' && elapsed > element.formationTime + element.displayTime) {
                    element.phase = 'returning';
                    // Start return journey for particles
                    element.particles.forEach(particle => {
                        particle.recruitmentState = 'returning_home';
                        particle.targetX = particle.originalX;
                        particle.targetY = particle.originalY;
                        particle.targetAlpha = 0.7; // Fade as they return
                    });
                    console.log('🔮 Particles returning to Clever\'s body');
                }
                
                // Update recruited particles with enhanced animation
                element.particles.forEach(particle => {
                    // Smooth recruitment animation
                    if (particle.recruitmentPhase < 1) {
                        particle.recruitmentPhase += particle.recruitmentSpeed;
                        particle.glowIntensity = Math.sin(particle.recruitmentPhase * Math.PI) * 0.5;
                    }
                    
                    // Enhanced corner glow for formed panels
                    if (element.phase === 'displaying') {
                        particle.pulsePhase += 0.08;
                        const pulse = Math.sin(particle.pulsePhase) * 0.3;
                        particle.size = (4 + Math.random()) + pulse;
                    }
                    
                    // Fade in/out based on phase
                    if (element.phase === 'recruiting' || element.phase === 'formed') {
                        if (particle.alpha < 0.9) particle.alpha += 0.08;
                    } else if (element.phase === 'returning') {
                        if (particle.alpha > 0) particle.alpha -= 0.05;
                    }
                });
                
                // Remove completed bubbles when particles have returned
                if (element.phase === 'returning' && 
                    element.particles.every(p => p.alpha <= 0.1)) {
                    // Release particles back to general population
                    element.particles.forEach(particle => {
                        particle.isRecruited = false;
                        particle.recruitmentState = null;
                        particle.chatBubbleCorner = null;
                        particle.color = particle.originalColor;
                        particle.size = particle.originalSize;
                        particle.isInFormation = false;
                    });
                    this.uiElements.delete(id);
                    console.log('🔮 Particles successfully returned to Clever\'s body');
                }
            } else if (element.type === 'dynamic_chat_panel') {
                const elapsed = Date.now() - element.createdAt;
                
                // Enhanced phase management: spawning -> forming -> glowing -> displaying -> pulsing -> dissolving
                if (element.phase === 'spawning' && elapsed > element.spawnTime) {
                    element.phase = 'forming';
                    console.log('💡 Dynamic panel particles spawned, now forming outline');
                } else if (element.phase === 'forming' && elapsed > element.spawnTime + element.formationTime) {
                    element.phase = 'glowing';
                    console.log('💡 Dynamic panel outline formed, adding glow');
                } else if (element.phase === 'glowing' && elapsed > element.spawnTime + element.formationTime + element.glowTime) {
                    element.phase = 'displaying';
                    console.log('💡 Dynamic panel glow complete, now displaying');
                } else if (element.phase === 'displaying' && elapsed > element.spawnTime + element.formationTime + element.glowTime + element.displayTime) {
                    element.phase = 'pulsing';
                    console.log('💡 Dynamic panel entering pulse phase');
                } else if (element.phase === 'pulsing' && elapsed > element.spawnTime + element.formationTime + element.glowTime + element.displayTime + element.pulseTime) {
                    element.phase = 'dissolving';
                    console.log('💡 Dynamic panel beginning dissolve');
                }
                
                // Update dynamic panel particles with enhanced animations
                element.particles.forEach((particle, index) => {
                    if (!particle.dynamicPanel) return;
                    
                    // Set formation targets based on outline shape and phase
                    if (element.phase === 'forming' || element.phase === 'glowing' || element.phase === 'displaying' || element.phase === 'pulsing') {
                        this.setDynamicPanelFormation(particle, index, element);
                    }
                    
                    // Phase-specific animations
                    if (element.phase === 'spawning') {
                        // Particles appear with fade-in
                        particle.alpha += 0.05;
                        particle.size += (particle.targetSize - particle.size) * 0.1;
                    } else if (element.phase === 'forming') {
                        // Particles move to outline positions
                        if (particle.formationPhase < 1) {
                            particle.formationPhase += particle.formationSpeed;
                        }
                        particle.alpha += (particle.targetAlpha - particle.alpha) * 0.08;
                    } else if (element.phase === 'glowing') {
                        // Add glow effect
                        particle.glowIntensity += (particle.targetGlowIntensity - particle.glowIntensity) * 0.1;
                        element.glowIntensity += (element.targetGlowIntensity - element.glowIntensity) * 0.1;
                    } else if (element.phase === 'displaying' || element.phase === 'pulsing') {
                        // Pulse animation based on domain pulse profile and mood/intensity
                        const prof = element.pulseProfile || { speed: 0.08, amplitude: 0.4, jitter: 0.02 };
                        const sp = (prof.speed * (element.pulseSpeedScale || 1));
                        particle.pulsePhase += sp + (Math.random() - 0.5) * prof.jitter;
                        const pulse = Math.sin(particle.pulsePhase) * (element.pulseIntensity || 0.3) * prof.amplitude;
                        particle.size = particle.targetSize + pulse * 2;
                        particle.glowIntensity = particle.targetGlowIntensity + pulse * 0.3;
                        
                        // Update element-level pulse for text rendering
                        element.pulsePhase = (element.pulsePhase || 0) + sp * 0.6;
                    } else if (element.phase === 'dissolving') {
                        // Dissolve effect: drift outward from panel center and fade
                        if (particle.dissolvePhase < 1) {
                            const cx = element.x + element.width / 2;
                            const cy = element.y + element.height / 2;
                            const dx = particle.x - cx;
                            const dy = particle.y - cy;
                            const len = Math.max(1, Math.hypot(dx, dy));
                            const nx = dx / len;
                            const ny = dy / len;
                            particle.x += nx * 0.8;
                            particle.y += ny * 0.8;
                            particle.dissolvePhase += 0.02;
                            particle.dissolvePhase += (element.dissolveSpeed || 0.02);
                            particle.alpha *= 0.95;
                            particle.size *= 0.985;
                            particle.glowIntensity *= 0.9;
                        }
                    }
                });
                
                // Remove completed dynamic panels when fully dissolved
                if (element.phase === 'dissolving' && 
                    element.particles.every(p => p.dissolvePhase >= 1 || p.alpha <= 0.1)) {
                    // Optional: leave a faint memory echo as a translucent after-image
                    this._leaveMemoryEcho(element);
                    // Release particles back to general population
                    element.particles.forEach(particle => {
                        particle.isRecruited = false;
                        particle.dynamicPanel = false;
                        particle.color = particle.originalColor;
                        particle.size = particle.originalSize;
                        particle.isInFormation = false;
                    });
                    this.uiElements.delete(id);
                    // Performance summary upon dissolve
                    const activePanels = Array.from(this.uiElements.values()).filter(e => e.type === 'dynamic_chat_panel').length;
                    const fps = Math.round(this._fpsEMA);
                    console.log(`💡 Panel dissolved | panels=${activePanels} | fps≈${fps} | mood=${element.mood} | domain=${element.knowledgeDomain}`);
                }
            } else if (element.type === 'input_bar') {
                // Maintain gentle breathing alpha and caret blink
                element.alpha += (element.targetAlpha - element.alpha) * 0.08;
                element.caretBlink = (element.caretBlink || 0) + 1;
                if (typeof element.focusGlow !== 'number') {
                    element.focusGlow = this.inputBarFocus ? 1 : 0;
                }
                if (typeof element.targetFocusGlow !== 'number') {
                    element.targetFocusGlow = this.inputBarFocusTarget;
                }
                element.focusGlow += (element.targetFocusGlow - element.focusGlow) * 0.12;
                element.focused = this.inputBarFocus;
                // Keep particles at rectangle corners
                const corners = [
                    { x: element.x, y: element.y },
                    { x: element.x + element.width, y: element.y },
                    { x: element.x + element.width, y: element.y + element.height },
                    { x: element.x, y: element.y + element.height }
                ];
                element.particles.forEach((p, i) => {
                    p.targetX = corners[i].x;
                    p.targetY = corners[i].y;
                    p.formationStrength = 0.18;
                });
            }
        });
    }
    
    /**
     * Set particle formation targets for dynamic panel outline
     * 
     * Why: Creates organic or rectangular outlines for enhanced visual feedback
     * Where: Called during dynamic panel formation phase
     * How: Distributes particles around panel perimeter based on shape preference
     */
    setDynamicPanelFormation(particle, index, element) {
        const { x, y, width, height, outlineShape } = element;
        const total = element.particles.length;
        
        let targetX, targetY;
        
        if (outlineShape === 'rectangular') {
            // Distribute particles around rectangle perimeter
            const perimeter = 2 * (width + height);
            const position = (index / total) * perimeter;
            
            if (position < width) {
                // Top edge
                targetX = x + position;
                targetY = y;
            } else if (position < width + height) {
                // Right edge
                targetX = x + width;
                targetY = y + (position - width);
            } else if (position < 2 * width + height) {
                // Bottom edge
                targetX = x + width - (position - width - height);
                targetY = y + height;
            } else {
                // Left edge
                targetX = x;
                targetY = y + height - (position - 2 * width - height);
            }

            // Add subtle jitter to avoid perfect rigidity while keeping rectangular feel
            const jitter = 0.6;
            targetX += (Math.random() - 0.5) * jitter;
            targetY += (Math.random() - 0.5) * jitter;
        } else {
            // Organic shape - slightly rounded rectangle with natural variation
            const angle = (index / total) * Math.PI * 2;
            const radiusX = width * 0.45;
            const radiusY = height * 0.45;
            const centerX = x + width / 2;
            const centerY = y + height / 2;
            
            // Add organic variation
            const variation = 0.1 + Math.sin(angle * 3) * 0.05;
            targetX = centerX + Math.cos(angle) * radiusX * (1 + variation);
            targetY = centerY + Math.sin(angle) * radiusY * (1 + variation);
        }
        
        particle.targetX = targetX;
        particle.targetY = targetY;
        particle.formationStrength = 0.08; // Smooth formation movement
    }
    
    /**
     * Render particle-formed UI elements with enhanced square visualization
     */
    renderParticleUI() {
    const toDelete = [];
    this.uiElements.forEach((element, id) => {
            if (element.type === 'chat_bubble') {
                // Draw connection lines between corner particles to form visible square
                if (element.phase === 'displaying' && element.particles.length === 4) {
                    this.ctx.save();
                    this.ctx.strokeStyle = element.particles[0].color;
                    this.ctx.globalAlpha = 0.4;
                    this.ctx.lineWidth = 1;
                    this.ctx.beginPath();
                    
                    // Connect the four corners in square formation
                    for (let i = 0; i < 4; i++) {
                        const current = element.particles[i];
                        const next = element.particles[(i + 1) % 4];
                        if (i === 0) {
                            this.ctx.moveTo(current.x, current.y);
                        }
                        this.ctx.lineTo(next.x, next.y);
                    }
                    this.ctx.closePath();
                    this.ctx.stroke();
                    this.ctx.restore();
                }
                
                // Render corner particles with enhanced glow
                element.particles.forEach(particle => {
                    this.ctx.save();
                    this.ctx.globalAlpha = particle.alpha;
                    
                    // Add glow effect for recruited particles
                    if (particle.isRecruited && element.phase === 'displaying') {
                        this.ctx.shadowColor = particle.color;
                        this.ctx.shadowBlur = 10;
                    }
                    
                    this.ctx.fillStyle = particle.color;
                    this.ctx.beginPath();
                    this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                    this.ctx.fill();
                    this.ctx.restore();
                });
                
                // Render text content within the particle square
                if (element.phase === 'displaying' && element.particles.length === 4) {
                    this.ctx.save();
                    this.ctx.globalAlpha = Math.min(0.9, element.particles[0].alpha);
                    this.ctx.fillStyle = '#ffffff';
                    this.ctx.font = '14px -apple-system, BlinkMacSystemFont, sans-serif';
                    this.ctx.textAlign = 'left';
                    this.ctx.textBaseline = 'top';
                    
                    // Calculate text area within the square
                    const minX = Math.min(...element.particles.map(p => p.x));
                    const maxX = Math.max(...element.particles.map(p => p.x));
                    const minY = Math.min(...element.particles.map(p => p.y));
                    const maxY = Math.max(...element.particles.map(p => p.y));
                    
                    const textX = minX + 10;
                    const textY = minY + 10;
                    const maxWidth = (maxX - minX) - 20;
                    
                    // Word wrap text within the square
                    const lines = this.wrapTextInto(this.ctx, element.message, maxWidth);
                    
                    // Draw text lines
                    lines.forEach((line, index) => {
                        this.ctx.fillText(line, textX, textY + (index * 18));
                    });
                    
                    this.ctx.restore();
                }
            } else if (element.type === 'dynamic_chat_panel') {
                // Render dynamic particle chat panel with enhanced visual effects
                
                // Domain gradient transition: blend from prior domain to current briefly
                if (this._lastRenderedDomain && this._lastRenderedDomain !== (element.knowledgeDomain || 'chat_interface')) {
                    const t = Math.min(1, (Date.now() - (element.createdAt || 0)) / 600); // ~0.6s transition
                    const grad = this.ctx.createLinearGradient(element.x, element.y, element.x + element.width, element.y + element.height);
                    const prevTheme = VISUAL_THEMES[this._lastRenderedDomain] || VISUAL_THEMES.chat_interface;
                    const currTheme = VISUAL_THEMES[element.knowledgeDomain || 'chat_interface'] || VISUAL_THEMES.chat_interface;
                    grad.addColorStop(0, prevTheme.colors[0]);
                    grad.addColorStop(t, currTheme.colors[0]);
                    this.ctx.save();
                    this.ctx.globalAlpha = 0.08;
                    this.ctx.fillStyle = grad;
                    this.ctx.fillRect(element.x - 2, element.y - 2, element.width + 4, element.height + 4);
                    this.ctx.restore();
                }
                this._lastRenderedDomain = element.knowledgeDomain || 'chat_interface';

                // Render outline particles with glow and pulse effects
                element.particles.forEach(particle => {
                    if (!particle.dynamicPanel) return;
                    
                    this.ctx.save();
                    this.ctx.globalAlpha = particle.alpha;
                    
                    // Enhanced glow effect based on energy and phase
                    if (particle.glowIntensity > 0) {
                        this.ctx.shadowColor = particle.color;
                        this.ctx.shadowBlur = 8 + particle.glowIntensity * 12;
                    }
                    
                    this.ctx.fillStyle = particle.color;
                    this.ctx.beginPath();
                    this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                    this.ctx.fill();
                    this.ctx.restore();
                });
                
                // Render text content with enhanced styling and glow (centered)
                if ((element.phase === 'displaying' || element.phase === 'pulsing') && element.particles.length > 0) {
                    this.ctx.save();
                    
                    // Calculate text area within the particle cluster
                    const avgAlpha = element.particles.reduce((sum, p) => sum + p.alpha, 0) / element.particles.length;
                    const textAlpha = Math.min(0.95, avgAlpha);
                    
                    // Enhanced text glow effect
                    const glowIntensity = element.glowIntensity || 0;
                    if (glowIntensity > 0) {
                        this.ctx.shadowColor = element.particles[0].color;
                        this.ctx.shadowBlur = 4 + glowIntensity * 8;
                    }
                    
                    // Pulse effect on text
                    const pulseEffect = element.pulsePhase ? Math.sin(element.pulsePhase) * element.pulseIntensity * 0.1 : 0;
                    this.ctx.globalAlpha = textAlpha + pulseEffect;
                    
                    this.ctx.fillStyle = '#ffffff';
                    this.ctx.font = '14px -apple-system, BlinkMacSystemFont, sans-serif';
                    this.ctx.textAlign = 'left';
                    this.ctx.textBaseline = 'top';
                    
                    const maxWidth = element.width - 24;
                    const lines = this.wrapTextInto(this.ctx, element.message, maxWidth);
                    const textHeight = lines.length * 18;
                    const textX = element.x + 12;
                    const textY = element.y + (element.height - textHeight) / 2; // vertically centered
                    
                    // Draw text lines with slight spacing
                    lines.forEach((line, index) => {
                        this.ctx.fillText(line, textX, textY + (index * 18));
                    });
                    
                    this.ctx.restore();
                }
                
                // Optional: Draw subtle connecting lines between outline particles for organic shapes
                if (element.outlineShape === 'organic' && element.phase === 'displaying' && element.particles.length > 3) {
                    this.ctx.save();
                    this.ctx.globalAlpha = 0.2;
                    this.ctx.strokeStyle = element.particles[0].color;
                    this.ctx.lineWidth = 1;
                    this.ctx.beginPath();
                    
                    // Connect particles in sequence for organic outline
                    for (let i = 0; i < element.particles.length; i++) {
                        const particle = element.particles[i];
                        if (i === 0) {
                            this.ctx.moveTo(particle.x, particle.y);
                        } else {
                            this.ctx.lineTo(particle.x, particle.y);
                        }
                    }
                    this.ctx.closePath();
                    this.ctx.stroke();
                    this.ctx.restore();
                }
            } else if (element.type === 'input_bar') {
                this.ctx.save();
                const focusGlow = Math.max(0, Math.min(1, element.focusGlow || 0));
                this.ctx.globalAlpha = element.alpha * (0.85 + focusGlow * 0.15);

                if (focusGlow > 0.05) {
                    this.ctx.shadowColor = `rgba(125, 217, 255, ${0.45 + focusGlow * 0.35})`;
                    this.ctx.shadowBlur = 10 + focusGlow * 18;
                } else {
                    this.ctx.shadowBlur = 0;
                }

                // Border via particle connections
                this.ctx.strokeStyle = focusGlow > 0.05 ? '#A5F3FF' : VISUAL_THEMES.chat_interface.colors[0];
                this.ctx.lineWidth = 1.2 + focusGlow * 1.3;
                this.ctx.beginPath();
                const pts = [
                    { x: element.x, y: element.y },
                    { x: element.x + element.width, y: element.y },
                    { x: element.x + element.width, y: element.y + element.height },
                    { x: element.x, y: element.y + element.height }
                ];
                this.ctx.moveTo(pts[0].x, pts[0].y);
                for (let i = 1; i <= 4; i++) {
                    const p = pts[i % 4];
                    this.ctx.lineTo(p.x, p.y);
                }
                this.ctx.stroke();

                // Fill
                const baseFill = focusGlow > 0.05 ? 0.68 : 0.55;
                this.ctx.fillStyle = `rgba(26,31,38,${baseFill})`;
                this.ctx.fillRect(element.x, element.y, element.width, element.height);

                // Text + caret
                const padding = 12;
                const textX = element.x + padding;
                const textY = element.y + element.height / 2 + 5;
                this.ctx.font = '15px Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial';
                this.ctx.fillStyle = '#CFFAFE';
                this.ctx.textBaseline = 'middle';
                const displayText = element.text || '';
                this.ctx.fillText(displayText, textX, textY);

                // Caret blink
                const caretVisible = element.focused && (Math.floor((element.caretBlink || 0) / 30) % 2 === 0); // ~0.5s
                if (caretVisible) {
                    const w = this.ctx.measureText(displayText).width;
                    this.ctx.beginPath();
                    this.ctx.moveTo(textX + w + 2, element.y + 8);
                    this.ctx.lineTo(textX + w + 2, element.y + element.height - 8);
                    this.ctx.strokeStyle = '#7DD3FC';
                    this.ctx.lineWidth = 1.2;
                    this.ctx.stroke();
                }

                this.ctx.restore();
            } else if (element.type === 'domain_transition') {
                const elapsed = Date.now() - element.createdAt;
                const t = Math.min(1, elapsed / element.duration);
                // Ease in-out for smoother perception
                const ease = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
                const alpha = 0.25 * (1 - ease);
                if (alpha <= 0.01) {
                    toDelete.push(id);
                } else {
                    this.ctx.save();
                    this.ctx.globalAlpha = alpha;
                    // Simple vertical gradient fill
                    const grad = this.ctx.createLinearGradient(0, 0, this.canvas.width, this.canvas.height);
                    grad.addColorStop(0, element.fromColor);
                    grad.addColorStop(1, element.toColor);
                    this.ctx.fillStyle = grad;
                    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                    this.ctx.restore();
                }
            } else if (element.type === 'memory_echo') {
                const age = Date.now() - (element.createdAt || 0);
                const life = element.lifespan || 900;
                if (age > life) {
                    toDelete.push(id);
                } else {
                    const k = 1 - Math.min(1, age / life);
                    const alpha = (element.alpha || 0.18) * k;
                    this.ctx.save();
                    this.ctx.globalAlpha = alpha;
                    this.ctx.strokeStyle = element.color || '#88C0D0';
                    this.ctx.lineWidth = 1;
                    this.ctx.fillStyle = 'transparent';
                    // Draw a subtle rounded rectangle outline where the panel was
                    const r = 10;
                    const x = element.x, y = element.y, w = element.width, h = element.height;
                    this.ctx.beginPath();
                    this.ctx.moveTo(x + r, y);
                    this.ctx.lineTo(x + w - r, y);
                    this.ctx.quadraticCurveTo(x + w, y, x + w, y + r);
                    this.ctx.lineTo(x + w, y + h - r);
                    this.ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
                    this.ctx.lineTo(x + r, y + h);
                    this.ctx.quadraticCurveTo(x, y + h, x, y + h - r);
                    this.ctx.lineTo(x, y + r);
                    this.ctx.quadraticCurveTo(x, y, x + r, y);
                    this.ctx.stroke();
                    this.ctx.restore();
                }
            }
        });
        // Cleanup finished overlays
        toDelete.forEach(id => this.uiElements.delete(id));
    }

    /**
     * Leave a faint translucent after-image to represent short-term memory echo.
     */
    _leaveMemoryEcho(element) {
        try {
            const now = Date.now();
            const echo = {
                type: 'memory_echo',
                x: element.x,
                y: element.y,
                width: element.width,
                height: element.height,
                color: (element.colors && element.colors[0]) || '#88C0D0',
                alpha: 0.18,
                createdAt: now,
                lifespan: 900, // fade out over ~0.9s
            };
            this.uiElements.set(`echo-${now}-${Math.floor(Math.random()*1000)}`, echo);
        } catch (e) {
            // non-fatal
        }
    }

    // Helpers
    wrapTextInto(ctx, text, maxWidth) {
        const words = String(text || '').split(/\s+/);
        const lines = [];
        let line = '';
        words.forEach(word => {
            const test = line ? `${line} ${word}` : word;
            if (ctx.measureText(test).width > maxWidth) {
                if (line) lines.push(line);
                line = word;
            } else {
                line = test;
            }
        });
        if (line) lines.push(line);
        return lines;
    }

    wrapTextLinesForSize(text, maxWidth) {
        const ctx = this.ctx;
        ctx.save();
        ctx.font = '14px -apple-system, BlinkMacSystemFont, sans-serif';
        const lines = this.wrapTextInto(ctx, text, maxWidth);
        let max = 0;
        lines.forEach(l => { max = Math.max(max, ctx.measureText(l).width); });
        ctx.restore();
        return { count: Math.max(1, lines.length), maxWidth: max };
    }
    
    /**
     * Set knowledge-driven particle mode with intelligent detection
     */
    setKnowledgeMode(knowledgeDomain) {
        if (VISUAL_THEMES[knowledgeDomain]) {
            const prev = this.activeKnowledgeDomain || 'chat_interface';
            this.activeKnowledgeDomain = knowledgeDomain;
            const theme = VISUAL_THEMES[knowledgeDomain];

            // Trigger domain transition gradient overlay
            this._triggerDomainTransition(prev, knowledgeDomain);

            // Update particles with knowledge colors
            this.particles.forEach(particle => {
                particle.color = theme.colors[Math.floor(Math.random() * theme.colors.length)];
                particle.energy = theme.energy;
            });
            
            console.log(`🧠 Particle system now reflecting ${knowledgeDomain} knowledge domain`);
        }
    }

    /**
     * Trigger a transient gradient overlay between two domains (~1.2s)
     */
    _triggerDomainTransition(fromDomain, toDomain) {
        try {
            const from = (VISUAL_THEMES[fromDomain] && VISUAL_THEMES[fromDomain].colors[0]) || '#69EACB';
            const to = (VISUAL_THEMES[toDomain] && VISUAL_THEMES[toDomain].colors[0]) || '#69EACB';
            const now = Date.now();
            this.uiElements.set(`domain-xfade-${now}`, {
                type: 'domain_transition',
                fromColor: from,
                toColor: to,
                createdAt: now,
                duration: 1200
            });
        } catch {}
    }
    
    resize(width, height) {
        const oldWidth = this.canvas.width;
        const oldHeight = this.canvas.height;
        
        this.canvas.width = width;
        this.canvas.height = height;
        
        // Scale particle positions
        const scaleX = width / oldWidth;
        const scaleY = height / oldHeight;
        
        this.particles.forEach(particle => {
            particle.x *= scaleX;
            particle.y *= scaleY;
            particle.targetX *= scaleX;
            particle.targetY *= scaleY;
        });
        
        console.log('Chamber resized to', width, 'x', height);
    }
    
    /**
     * Start Shape Rotation Sequence
     * 
     * Why: Provides mesmerizing 720° rotation (2 full rotations) for mathematical shapes
     * Where: Called after shape formation completes to showcase geometric beauty
     * How: Applies smooth rotation transformation to all mathematical shape particles
     */
    startShapeRotation() {
        // Find ALL mathematical shape particles
        const mathParticles = this.particles.filter(p => p.mathematicalPoint);
        console.log(`Found ${mathParticles.length} particles for 3D rotation`);
        
        if (mathParticles.length === 0) {
            console.warn('No mathematical particles found for rotation');
            return;
        }
        
        // Detect shape type to choose appropriate rotation
        const shapeType = this.currentShapeData?.name?.toLowerCase() || 'unknown';
        const isDNA = shapeType.includes('dna') || shapeType.includes('helix');
        
        console.log(`🎡 Starting 3D rotation for ${shapeType}: ${isDNA ? 'drill/screw style' : 'ferris wheel style'}`);
        
        // Store original positions from mathematical points
        mathParticles.forEach(particle => {
            if (particle.mathematicalPoint) {
                particle.originalTargetX = particle.mathematicalPoint.originalX;
                particle.originalTargetY = particle.mathematicalPoint.originalY;
                particle.originalTargetZ = particle.mathematicalPoint.originalZ || 0;
            }
        });
        
        // Rotation parameters
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const totalRotation = Math.PI * 4; // 720 degrees (2 full rotations)
        const rotationDuration = isDNA ? 6000 : 8000; // Faster for DNA (6s vs 8s)
        const startTime = Date.now();
        
        this.isRotatingShape = true;
        
        // Choose rotation style based on shape type
        const rotateShape = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / rotationDuration, 1);
            
            // Smooth easing
            const easeInOutQuad = t => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
            const easedProgress = easeInOutQuad(progress);
            
            const currentAngle = totalRotation * easedProgress;
            
            if (isDNA) {
                // DNA: Rotate around vertical Z-axis (like a drill/screw)
                mathParticles.forEach(particle => {
                    const relX = particle.originalTargetX - centerX;
                    const relY = particle.originalTargetY - centerY;
                    const relZ = particle.originalTargetZ || 0;
                    
                    // Rotation around Z-axis (drill motion) - X and Y rotate, Z stays same
                    const rotatedX = relX * Math.cos(currentAngle) - relY * Math.sin(currentAngle);
                    const rotatedY = relX * Math.sin(currentAngle) + relY * Math.cos(currentAngle);
                    
                    // Apply perspective for depth effect
                    const perspective = 800;
                    const projectedScale = perspective / (perspective + relZ);
                    
                    particle.targetX = centerX + (rotatedX * projectedScale);
                    particle.targetY = centerY + (rotatedY * projectedScale);
                    
                    // Depth-based scaling
                    const depthScale = 0.6 + (0.4 * projectedScale);
                    particle.scale = depthScale;
                });
            } else {
                // Other shapes: Ferris wheel rotation (around Y-axis)
                mathParticles.forEach(particle => {
                    const relX = particle.originalTargetX - centerX;
                    const relY = particle.originalTargetY - centerY;
                    const relZ = particle.originalTargetZ || 0;
                    
                    // 3D rotation around Y-axis (vertical ferris wheel motion)
                    // X and Z rotate, Y stays relatively the same
                    const rotatedX = relX * Math.cos(currentAngle) + relZ * Math.sin(currentAngle);
                    const rotatedZ = -relX * Math.sin(currentAngle) + relZ * Math.cos(currentAngle);
                    
                    // Apply perspective projection for 3D effect
                    const perspective = 800;
                    const projectedScale = perspective / (perspective + rotatedZ);
                    
                    particle.targetX = centerX + (rotatedX * projectedScale);
                    particle.targetY = centerY + (relY * projectedScale);
                    
                    // Add depth-based opacity/size effect (closer = brighter)
                    const depthScale = 0.6 + (0.4 * projectedScale);
                    particle.scale = depthScale;
                });
            }
            
            // Continue rotation until complete
            if (progress < 1) {
                requestAnimationFrame(rotateShape);
            } else {
                const rotationType = isDNA ? 'drill/screw motion' : 'ferris wheel motion';
                console.log(`✅ 3D rotation completed (720° ${rotationType})`);
                this.isRotatingShape = false;
                
                // Restore original positions
                mathParticles.forEach(particle => {
                    particle.targetX = particle.originalTargetX;
                    particle.targetY = particle.originalTargetY;
                    particle.scale = 1.0; // Reset scale
                });
            }
        };
        
        // Start rotation animation
        requestAnimationFrame(rotateShape);
    }
}

/**
 * Global initialization function
 */
window.startHolographicChamber = function(canvas) {
    try {
        if (!canvas || !(canvas instanceof HTMLCanvasElement)) {
            console.error('Invalid canvas provided to startHolographicChamber');
            return null;
        }
        
        const chamber = new HolographicChamber(canvas);
        chamber.setMode('idle');
        
        console.log('✅ Holographic chamber ready for cognitive visualization');
        return chamber;
        
    } catch (error) {
        console.error('Failed to start holographic chamber:', error);
        return null;
    }
};

console.log('🌟 Holographic Chamber engine loaded and ready');
