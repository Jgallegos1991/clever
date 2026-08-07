#!/usr/bin/env python3
"""
clever_visual_cognitive_engine.py - Clever's Permanent Visual Thinking Interface

Why: Provides Clever with sophisticated visual cognitive capabilities using her
     particle-dot-line system as a universal thinking and creation canvas that
     never goes away - becoming her permanent interface for all reasoning tasks
Where: Core visual cognition system integrated with decision engine and all cognitive processes
How: Advanced particle engine that renders thoughts, decisions, projects, and ideas visually

File Usage:
    - Called by: All cognitive systems needing visual representation or decision visualization
    - Key dependencies: clever_decision_engine.py, holographic-chamber.js, database.py
    - Visual contexts: Decision trees, project maps, brainstorming, IDE layouts, system diagrams
    - Canvas operations: Dynamic rendering, interactive visualization, real-time updates
"""

import json
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from clever_decision_engine import ActionSeverity, get_decision_engine, require_decision
from debug_config import get_debugger

debugger = get_debugger()


class VisualMode(Enum):
    """Visual rendering modes for different cognitive tasks"""

    DECISION_TREE = "decision_tree"  # Decision-making visualization
    PROJECT_MAP = "project_map"  # Code/project architecture
    BRAINSTORM = "brainstorm"  # Idea generation and connection
    SYSTEM_DIAGRAM = "system_diagram"  # System architecture visualization
    CUSTOM_IDE = "custom_ide"  # Clever's custom IDE layout
    MIND_MAP = "mind_map"  # Knowledge connection mapping
    DEBUG_FLOW = "debug_flow"  # Code execution flow visualization
    DESIGN_CANVAS = "design_canvas"  # UI/UX design workspace


@dataclass
class VisualNode:
    """A node in Clever's visual thinking space"""

    id: str
    x: float
    y: float
    z: float = 0.0
    label: str = ""
    node_type: str = "concept"
    color: str = "#00ff88"
    size: float = 1.0
    data: Dict[str, Any] = field(default_factory=dict)
    connections: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


@dataclass
class VisualConnection:
    """A connection between nodes in Clever's thinking space"""

    id: str
    from_node: str
    to_node: str
    connection_type: str = "thought"
    strength: float = 1.0
    color: str = "#00ff88"
    animated: bool = True
    bidirectional: bool = False
    label: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VisualCanvas:
    """Clever's visual thinking canvas"""

    id: str
    title: str
    mode: VisualMode
    nodes: Dict[str, VisualNode] = field(default_factory=dict)
    connections: Dict[str, VisualConnection] = field(default_factory=dict)
    viewport: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 10})
    created_at: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CleverVisualCognitiveEngine:
    """
    Clever's permanent visual cognitive interface using particle system

    Why: Provides sophisticated visual thinking capabilities that never go away,
         becoming Clever's universal interface for reasoning, creation, and decision-making
    Where: Core cognitive system integrated with all of Clever's thinking processes
    How: Advanced particle-based visualization with dynamic canvas management
    """

    def __init__(self):
        """Initialize Clever's visual cognitive engine"""
        self._lock = threading.RLock()
        self._canvases: Dict[str, VisualCanvas] = {}
        self._active_canvas_id: Optional[str] = None
        self._particle_engine_active = True

        # Visual cognitive templates
        self._templates = self._initialize_templates()

        debugger.info(
            "visual_engine",
            "Clever visual cognitive engine initialized - particles permanent",
        )

    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialize visual templates for different cognitive tasks"""
        return {
            "decision_tree": {
                "root_color": "#ff6b6b",
                "option_color": "#4ecdc4",
                "consequence_color": "#45b7d1",
                "connection_type": "decision_flow",
            },
            "project_map": {
                "file_color": "#96ceb4",
                "module_color": "#feca57",
                "connection_color": "#ff9ff3",
                "connection_type": "dependency",
            },
            "brainstorm": {
                "idea_color": "#00d2d3",
                "connection_color": "#ff9ff3",
                "highlight_color": "#ffbe76",
                "connection_type": "association",
            },
            "custom_ide": {
                "panel_color": "#2d3436",
                "editor_color": "#00b894",
                "tool_color": "#e17055",
                "connection_type": "layout",
            },
        }

    def create_decision_visualization(self, decision_context: Dict[str, Any]) -> str:
        """
        Create visual representation of a decision process

        Why: Enables Clever to visually represent decision-making like the reference mentioned
        Where: Called by decision engine to show choice processes visually
        How: Creates nodes for options and connections showing relationships and consequences
        """
        canvas_id = f"decision_{int(time.time())}"
        canvas = VisualCanvas(
            id=canvas_id,
            title=f"Decision: {decision_context.get('action_type', 'Unknown')}",
            mode=VisualMode.DECISION_TREE,
        )

        template = self._templates["decision_tree"]

        # Create root decision node
        root_node = VisualNode(
            id="root",
            x=0,
            y=0,
            z=0,
            label=decision_context.get("description", "Decision Point"),
            node_type="decision_root",
            color=template["root_color"],
            size=1.5,
        )
        canvas.nodes["root"] = root_node

        # Create option nodes
        options = [
            {"id": "allow", "label": "Allow Action", "x": -2, "y": 2},
            {"id": "deny", "label": "Deny Action", "x": 2, "y": 2},
            {"id": "defer", "label": "Defer Action", "x": 0, "y": 4},
        ]

        for option in options:
            option_node = VisualNode(
                id=option["id"],
                x=option["x"],
                y=option["y"],
                z=0,
                label=option["label"],
                node_type="decision_option",
                color=template["option_color"],
                size=1.2,
            )
            canvas.nodes[option["id"]] = option_node

            # Connect to root
            connection = VisualConnection(
                id=f"root_to_{option['id']}",
                from_node="root",
                to_node=option["id"],
                connection_type=template["connection_type"],
                animated=True,
            )
            canvas.connections[connection.id] = connection

        # Add consequence nodes
        consequences = [
            {
                "from": "allow",
                "label": "System Impact",
                "x": -3,
                "y": 4,
                "color": "#e74c3c",
            },
            {
                "from": "allow",
                "label": "Performance Effect",
                "x": -1,
                "y": 4,
                "color": "#f39c12",
            },
            {
                "from": "deny",
                "label": "User Experience",
                "x": 3,
                "y": 4,
                "color": "#27ae60",
            },
            {
                "from": "deny",
                "label": "Safety Maintained",
                "x": 1,
                "y": 4,
                "color": "#2ecc71",
            },
        ]

        for i, cons in enumerate(consequences):
            cons_node = VisualNode(
                id=f"consequence_{i}",
                x=cons["x"],
                y=cons["y"],
                z=0,
                label=cons["label"],
                node_type="consequence",
                color=cons["color"],
                size=0.8,
            )
            canvas.nodes[cons_node.id] = cons_node

            # Connect to option
            connection = VisualConnection(
                id=f"{cons['from']}_to_consequence_{i}",
                from_node=cons["from"],
                to_node=cons_node.id,
                connection_type="consequence_flow",
                strength=0.7,
                animated=True,
            )
            canvas.connections[connection.id] = connection

        self._canvases[canvas_id] = canvas
        self._active_canvas_id = canvas_id

        debugger.info("visual_engine", f"Decision visualization created: {canvas_id}")
        return canvas_id

    def create_project_visualization(self, project_structure: Dict[str, Any]) -> str:
        """
        Create visual map of project/code structure

        Why: Enables Clever to visualize code architecture and file relationships
        Where: Called when analyzing codebases or planning project modifications
        How: Creates nodes for files/modules with connections showing dependencies
        """
        canvas_id = f"project_{int(time.time())}"
        canvas = VisualCanvas(
            id=canvas_id,
            title=f"Project: {project_structure.get('name', 'Unknown')}",
            mode=VisualMode.PROJECT_MAP,
        )

        template = self._templates["project_map"]

        # Create nodes for each file/component
        files = project_structure.get("files", [])
        for i, file_info in enumerate(files):
            angle = (i / len(files)) * 2 * 3.14159  # Circular layout
            radius = 3

            file_node = VisualNode(
                id=file_info["name"],
                x=radius * 1.5 * (i % 3 - 1),  # Grid-like layout
                y=radius * 1.5 * (i // 3 - len(files) // 6),
                z=0,
                label=file_info["name"],
                node_type="file",
                color=(
                    template["file_color"]
                    if file_info.get("type") == "file"
                    else template["module_color"]
                ),
                size=1.0 + (file_info.get("importance", 0) * 0.5),
                data=file_info,
            )
            canvas.nodes[file_info["name"]] = file_node

        # Create connections for dependencies
        for file_info in files:
            for dependency in file_info.get("dependencies", []):
                if dependency in canvas.nodes:
                    connection = VisualConnection(
                        id=f"{file_info['name']}_to_{dependency}",
                        from_node=file_info["name"],
                        to_node=dependency,
                        connection_type=template["connection_type"],
                        color=template["connection_color"],
                        animated=True,
                    )
                    canvas.connections[connection.id] = connection

        self._canvases[canvas_id] = canvas
        self._active_canvas_id = canvas_id

        debugger.info("visual_engine", f"Project visualization created: {canvas_id}")
        return canvas_id

    def create_brainstorm_canvas(self, topic: str, initial_ideas: List[str] = None) -> str:
        """
        Create brainstorming canvas for idea generation

        Why: Provides Clever with visual space for creative thinking and idea connection
        Where: Called when exploring concepts, planning features, or problem-solving
        How: Creates dynamic canvas with idea nodes and connection discovery
        """
        canvas_id = f"brainstorm_{int(time.time())}"
        canvas = VisualCanvas(
            id=canvas_id, title=f"Brainstorm: {topic}", mode=VisualMode.BRAINSTORM
        )

        template = self._templates["brainstorm"]

        # Central topic node
        topic_node = VisualNode(
            id="topic",
            x=0,
            y=0,
            z=0,
            label=topic,
            node_type="central_topic",
            color=template["highlight_color"],
            size=2.0,
        )
        canvas.nodes["topic"] = topic_node

        # Initial idea nodes
        if initial_ideas:
            for i, idea in enumerate(initial_ideas):
                angle = (i / len(initial_ideas)) * 2 * 3.14159
                radius = 3

                idea_node = VisualNode(
                    id=f"idea_{i}",
                    x=radius * (0.5 + 0.3 * (i % 2)) * (1 if i % 4 < 2 else -1),
                    y=radius * (0.5 + 0.3 * ((i // 2) % 2)) * (1 if i % 8 < 4 else -1),
                    z=0,
                    label=idea,
                    node_type="idea",
                    color=template["idea_color"],
                    size=1.0,
                )
                canvas.nodes[idea_node.id] = idea_node

                # Connect to topic
                connection = VisualConnection(
                    id=f"topic_to_idea_{i}",
                    from_node="topic",
                    to_node=idea_node.id,
                    connection_type=template["connection_type"],
                    color=template["connection_color"],
                    animated=True,
                )
                canvas.connections[connection.id] = connection

        self._canvases[canvas_id] = canvas
        self._active_canvas_id = canvas_id

        debugger.info("visual_engine", f"Brainstorm canvas created: {canvas_id}")
        return canvas_id

    def design_custom_ide_layout(self, requirements: Dict[str, Any]) -> str:
        """
        Let Clever design her own IDE layout visually

        Why: Enables Clever to create custom development environment layouts
        Where: Called when Clever wants to design optimal IDE configuration
        How: Creates visual representation of IDE panels, tools, and workflows
        """
        canvas_id = f"ide_design_{int(time.time())}"
        canvas = VisualCanvas(
            id=canvas_id, title="Clever's Custom IDE Design", mode=VisualMode.CUSTOM_IDE
        )

        template = self._templates["custom_ide"]

        # Core IDE components
        components = [
            {"id": "editor", "label": "Code Editor", "x": 0, "y": 0, "type": "editor"},
            {"id": "terminal", "label": "Terminal", "x": 0, "y": -3, "type": "tool"},
            {
                "id": "file_tree",
                "label": "File Explorer",
                "x": -4,
                "y": 0,
                "type": "panel",
            },
            {"id": "debug", "label": "Debug Panel", "x": 4, "y": 0, "type": "tool"},
            {
                "id": "particle_viz",
                "label": "Particle Visualization",
                "x": 0,
                "y": 3,
                "type": "panel",
            },
            {
                "id": "decision_tree",
                "label": "Decision Engine",
                "x": -2,
                "y": 3,
                "type": "tool",
            },
            {
                "id": "system_monitor",
                "label": "System Monitor",
                "x": 2,
                "y": 3,
                "type": "tool",
            },
        ]

        for comp in components:
            comp_node = VisualNode(
                id=comp["id"],
                x=comp["x"],
                y=comp["y"],
                z=0,
                label=comp["label"],
                node_type=comp["type"],
                color=template[f"{comp['type']}_color"],
                size=1.5,
                data={"component_type": comp["type"]},
            )
            canvas.nodes[comp["id"]] = comp_node

        # Create layout connections
        layout_connections = [
            ("editor", "terminal", "workflow"),
            ("editor", "debug", "development"),
            ("file_tree", "editor", "navigation"),
            ("particle_viz", "decision_tree", "cognitive"),
            ("system_monitor", "debug", "monitoring"),
        ]

        for from_comp, to_comp, conn_type in layout_connections:
            connection = VisualConnection(
                id=f"{from_comp}_to_{to_comp}",
                from_node=from_comp,
                to_node=to_comp,
                connection_type=conn_type,
                color=template["connection_type"],
                animated=True,
                bidirectional=True,
            )
            canvas.connections[connection.id] = connection

        self._canvases[canvas_id] = canvas
        self._active_canvas_id = canvas_id

        debugger.info("visual_engine", f"Custom IDE layout designed: {canvas_id}")
        return canvas_id

    def get_canvas_for_frontend(self, canvas_id: str = None) -> Dict[str, Any]:
        """
        Get canvas data formatted for frontend particle engine

        Why: Provides frontend with visual data for particle rendering
        Where: Called by web interface to display Clever's visual thoughts
        How: Converts internal canvas format to particle engine format
        """
        if canvas_id is None:
            canvas_id = self._active_canvas_id

        if not canvas_id or canvas_id not in self._canvases:
            return {"nodes": [], "connections": [], "mode": "idle"}

        canvas = self._canvases[canvas_id]

        # Convert to frontend format
        frontend_data = {
            "mode": canvas.mode.value,
            "title": canvas.title,
            "nodes": [
                {
                    "id": node.id,
                    "x": node.x,
                    "y": node.y,
                    "z": node.z,
                    "label": node.label,
                    "type": node.node_type,
                    "color": node.color,
                    "size": node.size,
                    "data": node.data,
                }
                for node in canvas.nodes.values()
            ],
            "connections": [
                {
                    "id": conn.id,
                    "from": conn.from_node,
                    "to": conn.to_node,
                    "type": conn.connection_type,
                    "strength": conn.strength,
                    "color": conn.color,
                    "animated": conn.animated,
                    "bidirectional": conn.bidirectional,
                    "label": conn.label,
                }
                for conn in canvas.connections.values()
            ],
            "viewport": canvas.viewport,
            "timestamp": canvas.last_modified,
        }

        return frontend_data

    def list_canvases(self) -> List[Dict[str, Any]]:
        """List all available visual canvases"""
        return [
            {
                "id": canvas.id,
                "title": canvas.title,
                "mode": canvas.mode.value,
                "created_at": canvas.created_at,
                "last_modified": canvas.last_modified,
                "node_count": len(canvas.nodes),
                "connection_count": len(canvas.connections),
            }
            for canvas in self._canvases.values()
        ]


# Global visual engine instance
_visual_engine = None


def get_visual_engine() -> CleverVisualCognitiveEngine:
    """Get shared visual cognitive engine instance"""
    global _visual_engine
    if _visual_engine is None:
        _visual_engine = CleverVisualCognitiveEngine()
    return _visual_engine


def visualize_decision(decision_context: Dict[str, Any]) -> str:
    """Convenient function to create decision visualization"""
    engine = get_visual_engine()
    return engine.create_decision_visualization(decision_context)


def visualize_project(project_structure: Dict[str, Any]) -> str:
    """Convenient function to create project visualization"""
    engine = get_visual_engine()
    return engine.create_project_visualization(project_structure)


def brainstorm_visual(topic: str, ideas: List[str] = None) -> str:
    """Convenient function to create brainstorm canvas"""
    engine = get_visual_engine()
    return engine.create_brainstorm_canvas(topic, ideas)
