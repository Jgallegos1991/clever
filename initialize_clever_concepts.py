#!/usr/bin/env python3
"""
initialize_clever_concepts.py - Initialize Clever's Knowledge Base with Core Concepts

Why: Populates Clever's database with essential ideas including device security,
     containerization knowledge, and user-mentioned concepts for future development
Where: Run once to seed Clever's knowledge base with foundational concepts
How: Uses database methods to store ideas, technical concepts, and security requirements
"""

import time

from database import get_db_manager


def initialize_device_security_concepts():
    """Initialize device security and containment concepts"""
    print("🔒 Initializing Device Security Concepts...")

    db = get_db_manager()

    # Enforce device containment immediately
    db.enforce_device_containment("chromebook_primary")

    # Add device security ideas
    security_ideas = [
        {
            "category": "device_security",
            "title": "ChromeBook Data Containment",
            "description": "Everything must stay on the ChromeBook device - no USB device data transfer",
            "concept_data": "Critical security requirement to prevent data leakage to external devices",
            "priority": 5,
            "tags": ["security", "containment", "chromebook", "critical"],
        },
        {
            "category": "device_security",
            "title": "USB Device Monitoring",
            "description": "Monitor connected USB devices but prevent any data transfer to them",
            "concept_data": "Jay has connected USB devices but Clever's data must never leave the ChromeBook",
            "priority": 5,
            "tags": ["usb", "monitoring", "data_boundaries", "critical"],
        },
        {
            "category": "digital_sovereignty",
            "title": "Complete Local Control",
            "description": "Maintain total digital sovereignty with all processing and storage local",
            "concept_data": "No external dependencies, all Clever functionality must work offline",
            "priority": 5,
            "tags": ["sovereignty", "offline", "local", "independence"],
        },
    ]

    for idea in security_ideas:
        db.store_clever_idea(**idea)
        print(f"  ✅ Added: {idea['title']}")

    return len(security_ideas)


def initialize_containerization_knowledge():
    """Initialize containerization and Docker concepts for future self-healing"""
    print("\n🐳 Initializing Containerization Knowledge...")

    db = get_db_manager()

    container_concepts = [
        {
            "concept_name": "Containerization Fundamentals",
            "concept_type": "containerization",
            "description": "Understanding of process isolation, resource management, and application packaging",
            "technical_details": "Containers provide lightweight virtualization using kernel namespaces and cgroups",
            "use_cases": "Self-healing, code isolation, environment management, dependency containment",
            "priority": 4,
        },
        {
            "concept_name": "Docker Architecture",
            "concept_type": "docker",
            "description": "Docker engine, images, containers, and orchestration concepts",
            "technical_details": "Docker daemon, REST API, layered filesystem, container runtime",
            "use_cases": "Self-repair containers, code testing isolation, development environment management",
            "priority": 4,
        },
        {
            "concept_name": "Process Isolation",
            "concept_type": "isolation",
            "description": "Understanding how to isolate processes and manage resource boundaries",
            "technical_details": "Namespaces, cgroups, chroot, seccomp, capabilities",
            "use_cases": "Self-contained execution, safe code testing, resource management",
            "priority": 3,
        },
        {
            "concept_name": "Container Self-Healing",
            "concept_type": "self_healing",
            "description": "Using containers for automatic recovery and self-repair mechanisms",
            "technical_details": "Health checks, restart policies, rollback strategies, state management",
            "use_cases": "Clever fixing herself, automatic recovery from errors, safe code updates",
            "priority": 4,
        },
        {
            "concept_name": "Dependency Management",
            "concept_type": "containerization",
            "description": "Managing code dependencies and environment isolation",
            "technical_details": "Image layers, package management, environment variables, volume mounts",
            "use_cases": "Clean development environments, dependency isolation, reproducible builds",
            "priority": 3,
        },
    ]

    for concept in container_concepts:
        db.add_knowledge_concept(**concept)
        print(f"  ✅ Added: {concept['concept_name']}")

    return len(container_concepts)


def initialize_future_ideas():
    """Initialize future development ideas and concepts"""
    print("\n💡 Initializing Future Development Ideas...")

    db = get_db_manager()

    future_ideas = [
        {
            "category": "self_improvement",
            "title": "Container-Based Self-Healing",
            "description": "Use containerization concepts for Clever to fix her own code safely",
            "concept_data": "Clever could use container isolation to test fixes before applying them",
            "priority": 4,
            "tags": ["self_healing", "containers", "safety", "future"],
        },
        {
            "category": "development_tools",
            "title": "Isolated Code Testing",
            "description": "Use container-like isolation for testing code changes safely",
            "concept_data": "Test modifications in isolation before applying to main system",
            "priority": 3,
            "tags": ["testing", "isolation", "safety", "development"],
        },
        {
            "category": "particle_interface",
            "title": "Permanent Visual Cognitive Interface",
            "description": "Particle system as Clever's permanent thinking and creation canvas",
            "concept_data": "Never remove particles - universal interface for decisions, projects, brainstorming",
            "priority": 5,
            "tags": ["particles", "permanent", "visual", "cognitive", "interface"],
        },
        {
            "category": "database_enhancement",
            "title": "Environmental Awareness System",
            "description": "Clever understanding her hardware environment for optimization",
            "concept_data": "System monitoring for adaptive behavior and resource optimization",
            "priority": 4,
            "tags": ["environment", "optimization", "hardware", "awareness"],
        },
        {
            "category": "decision_making",
            "title": "Visual Decision Engine",
            "description": "Decision-making with visual representation of choices and consequences",
            "concept_data": "Particle-based decision trees showing options, risks, and outcomes",
            "priority": 4,
            "tags": ["decisions", "visual", "particles", "reasoning"],
        },
    ]

    for idea in future_ideas:
        db.store_clever_idea(**idea)
        print(f"  ✅ Added: {idea['title']}")

    return len(future_ideas)


def show_stored_concepts():
    """Display what concepts have been stored"""
    print("\n📊 Stored Concepts Summary...")

    db = get_db_manager()

    # Show ideas by category
    categories = [
        "device_security",
        "digital_sovereignty",
        "self_improvement",
        "development_tools",
        "particle_interface",
        "database_enhancement",
        "decision_making",
    ]

    for category in categories:
        ideas = db.get_clever_ideas(category=category)
        if ideas:
            print(f"\n  {category.upper()}:")
            for idea in ideas:
                print(f"    • {idea['title']} (Priority: {idea['priority']})")

    # Show knowledge concepts
    print(f"\n  TECHNICAL KNOWLEDGE:")
    concepts = db.get_knowledge_concepts()
    for concept in concepts:
        print(
            f"    • {concept['concept_name']} ({concept['concept_type']}) - Priority: {concept['learning_priority']}"
        )


if __name__ == "__main__":
    print("🧠 Initializing Clever's Knowledge Base with Core Concepts")
    print("=" * 65)

    try:
        # Initialize all concept categories
        security_count = initialize_device_security_concepts()
        container_count = initialize_containerization_knowledge()
        idea_count = initialize_future_ideas()

        total_concepts = security_count + container_count + idea_count

        print(f"\n✅ Initialization Complete!")
        print(f"   📋 {security_count} Security Concepts")
        print(f"   🐳 {container_count} Container Concepts")
        print(f"   💡 {idea_count} Future Ideas")
        print(f"   🎯 {total_concepts} Total Concepts")

        # Show what was stored
        show_stored_concepts()

        print(f"\n🎉 Clever's knowledge base is now populated with:")
        print(f"   • Device security and containment requirements")
        print(f"   • Containerization knowledge for future self-healing")
        print(f"   • Future development ideas and concepts")
        print(f"   • All stored in her permanent database for future use!")

    except Exception as e:
        print(f"❌ Error initializing concepts: {e}")
        import traceback

        traceback.print_exc()
