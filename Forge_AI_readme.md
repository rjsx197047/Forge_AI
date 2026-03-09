# Pulse AI --- Agentic AI Workforce Platform

## Overview

Pulse AI is a platform that allows a user to create and manage a team of
autonomous AI agents that run tasks continuously. The system acts like a
digital company where the user is the CEO and agents are workers that
can run jobs simultaneously.

The platform will:

- Start with **0 agents**
- Allow users to **create agents dynamically**
- Allow users to **assign tasks**
- Run agents **simultaneously**
- Display agents in a **Mission Control UI**
- Save results as **.md files**
- Allow interaction through **UI, Telegram, and terminal chat**
- Display a **pixel office visualization** showing agents working in real-time

> For the detailed technical specification of the Pixel Office visualization system, see the [Advanced Pixel Office Technical Specification](./Forge_AI_advanced_pixel_office_readme.md).

------------------------------------------------------------------------

# System Architecture

    User → Mission Control UI → Pulse Core → Agent Manager → Parallel Agents → Tasks → Tools → Results

Core components:

-   Mission Control UI
-   Pulse Core Backend
-   Agent Manager
-   Task Queue
-   Agent Workers
-   Memory + Output System
-   Telegram Interface

------------------------------------------------------------------------

# Development Phases

## Phase 1 --- Core Backend (Foundation)

Goal: Build the core system that can create and run agents
simultaneously.

Tasks:

1.  Create project structure

    pulse-ai/
    │
    ├─ core/
    │   orchestrator.py
    │   agent_manager.py
    │   scheduler.py
    │
    ├─ agents/
    │
    ├─ memory/
    │
    ├─ outputs/
    │
    ├─ logs/
    │
    ├─ ui/
    │
    └─ telegram/

2.  Build the **Agent Manager**

Functions:

-   create_agent()
-   delete_agent()
-   start_agent()
-   stop_agent()
-   assign_task()

Agent structure:

    Agent:
      name
      role
      model
      status
      task_queue
      memory

3.  Implement **agent registry**

Agents stored as folders:

    agents/
       researcher/
          config.json
          memory.md
          tasks.json

4.  Implement **parallel agent workers**

Agents run simultaneously using async workers.

Pseudo loop:

    while agent_active:
        check task queue
        if task:
            run AI model
            save result
        update status

5.  Implement **task system**

Each agent has a queue:

    tasks = [
      "research AI startups",
      "analyze competitors"
    ]

------------------------------------------------------------------------

# Phase 2 --- Output & Memory System

Goal: Agents store information and produce reports.

Create directories:

    memory/
    outputs/
    logs/

Example output:

    outputs/researcher/task_01.md

Example content:

    # Research Report

    Top AI startups:

    1. Company A
    2. Company B

Memory files allow agents to remember context.

------------------------------------------------------------------------

# Phase 3 --- Mission Control UI

Goal: Create a dashboard to control the system.

Features:

Agent Dashboard

Displays:

-   agent name
-   role
-   status
-   active tasks

Example display:

    Researcher   🟢 Working
    Coder        🔴 Idle
    Writer       🟡 Thinking

Agent Control Panel:

User can:

-   Create agent
-   Delete agent
-   Assign task
-   View outputs (see Outputs Tab below)
-   View logs

### Outputs Tab

The Outputs tab provides a dedicated interface for browsing and managing agent-generated reports.

**Organization by Agent:**

Reports are grouped by agent in a folder-like structure:

    Researcher/
      task_01_ai_startups.md
      task_02_competitor_analysis.md
    Coder/
      task_01_feature_implementation.md
    Writer/
      task_01_blog_post.md

**Report Viewer:**

-   Click any .md file to view rendered Markdown
-   Syntax highlighting for code blocks
-   Support for tables, lists, and headers
-   Full-width readable layout

**Search & Filter:**

-   Search by agent name
-   Search within report content
-   Filter by date created
-   Sort by most recent

**Output Metadata:**

Each output displays:

-   Agent name
-   Task name / ID
-   Timestamp completed
-   File size
-   Task duration

**Quick Actions:**

-   Download as .md file
-   Copy to clipboard
-   Share via Telegram (Phase 6 integration)
-   Delete output

**UI Layout:**

    ┌─────────────────────────────────────────────┐
    │  Outputs Tab                                │
    ├──────────────┬──────────────────────────────┤
    │              │                              │
    │  Agents      │  Report Preview              │
    │  ────────    │  ───────────────             │
    │              │                              │
    │  Researcher  │  # Research Report           │
    │    3 reports │                              │
    │              │  Top AI startups:            │
    │  Coder       │  1. Company A                │
    │    1 report  │  2. Company B                │
    │              │                              │
    │  Writer      │  [Rendered Markdown]         │
    │    2 reports │                              │
    │              │                              │
    └──────────────┴──────────────────────────────┘

**Implementation Notes:**

-   Reports stored in `/outputs/{agent_name}/task_{id}.md`
-   Frontend reads from API endpoints
-   Markdown rendering via react-markdown or similar
-   Updates in real-time as agents complete tasks

Backend API:

    POST /create_agent
    POST /assign_task
    GET  /agents
    GET  /outputs                       # List all outputs
    GET  /outputs/{agent_name}          # Outputs for specific agent
    GET  /outputs/{agent_name}/{id}     # Specific output file
    DELETE /outputs/{agent_name}/{id}   # Delete output

------------------------------------------------------------------------

# Phase 4 --- Agent Creation UI

Allow users to dynamically create agents.

Form fields:

-   Agent Name
-   Role
-   AI Model
-   Optional Schedule
-   Tools

Example payload:

    {
      "name": "TrendScout",
      "role": "Find trending topics",
      "model": "gpt"
    }

Backend creates:

    agents/trendscout/config.json

Agent automatically launches worker.

------------------------------------------------------------------------

# Phase 5 --- Office Visualization (Pixel Office)

Goal: Create an animated pixel office interface where AI agents are visualized as workers in a digital workplace.

> **Full Technical Specification:** See the [Advanced Pixel Office Technical Specification](./Forge_AI_advanced_pixel_office_readme.md) for detailed architecture, data flow, and implementation reference.

### Concept

Instead of a traditional dashboard grid, agents exist inside a **visual office simulation**. Each agent is a visible worker that moves between desks, idle areas, and delivery zones based on its current state.

### Agent States

| State        | Behavior                           | Color  |
|--------------|-------------------------------------|--------|
| **Idle**     | Wanders in common area              | Red    |
| **Thinking** | Stands near assigned desk           | Yellow |
| **Working**  | Sits at desk, actively processing   | Green  |
| **Complete** | Returns to lounge / common area     | Blue   |
| **Offline**  | Not visible or grayed out           | Gray   |

### Visual Components

1. **Office Layout** --- Grid background with tile pattern, desk zones, common area at bottom
2. **Agent Sprites** --- 18x18 pixel workers, color-coded by state, smooth CSS transitions
3. **Desk System** --- Fixed desk positions where agents sit when working
4. **Movement** --- Agents transition positions based on state changes (1s CSS animations)

### Technical Implementation

**Frontend Components:**

    OfficeVisualization/
      OfficeCanvas.jsx        # Main container
      WorkerSprite.jsx        # Individual agent sprite
      DeskComponent.jsx       # Desk objects
      AgentInfoPanel.jsx      # Click-to-view details

**Real-time Updates (WebSocket recommended):**

    ws://localhost:8000/ws/office

    {
      "agent_id": "researcher_01",
      "state": "working",
      "desk": 1,
      "current_task": "Analyzing AI trends"
    }

**Polling Alternative (simpler):**

    GET /agents/status       # Poll every 2-3 seconds

### User Interactions

-   **Click Agent** --- Shows agent details, current task, task history
-   **Click Desk** --- Shows desk occupancy, assigned agents
-   **Add Agent** --- Creates new agent, spawns sprite in idle area

### Integration with Other Phases

-   **Phase 2 (Outputs):** Visual indicator when agent saves an output
-   **Phase 3 (Mission Control):** Office view as a tab alongside the dashboard and Outputs tab
-   **Phase 6 (Telegram):** Visual "delivery zone" animation when outputs are sent to Telegram
-   **Phase 8 (Scheduling):** Scheduled tasks trigger automatic agent movement

### Implementation Tiers

**MVP:** Static desks, square sprites with color states, polling updates, basic CSS transitions

**Enhanced:** WebSocket real-time updates, sprite-based walking animations, click interactions

**Advanced:** Agent pathfinding, multiple office rooms, day/night cycle, agent avatars

### Prototype

A working HTML/JS prototype is included in the [Advanced Pixel Office Technical Specification](./Forge_AI_advanced_pixel_office_readme.md). It demonstrates multi-agent simulation, state-based movement, and dynamic agent creation. The prototype serves as a starting point for the production React implementation.

------------------------------------------------------------------------

# Phase 6 --- Telegram Interface

Goal: Enable remote control and output delivery via Telegram.

### Command Interface

Telegram bot commands:

    /agents          # List all agents and their status
    /create_agent    # Create a new agent
    /task            # Assign task to agent
    /status          # Get system status
    /outputs         # List recent outputs

Example:

    /task researcher Find AI startup trends

Bot sends command to Pulse backend via webhook.

### Output Delivery

Agents can push completed reports directly to Telegram.

**Automatic Notifications:**

When an agent completes a task, the bot sends:

    Researcher completed: "AI Startup Analysis"

    Report available in Outputs tab
    Send report? /send_output researcher task_01

**Manual Retrieval:**

    /send_output researcher task_01

Bot sends formatted .md content or file attachment depending on report length.

**Configuration:**

-   Agents can have an `auto_notify` setting in their config
-   User can subscribe to specific agent completions
-   Short reports sent as messages, long reports sent as file attachments

### Integration with Outputs Tab

Telegram commands connect to the same backend endpoints as the Outputs tab (Phase 3):

-   `GET /outputs` maps to the `/outputs` command
-   `GET /outputs/{agent}/{id}` maps to `/send_output`
-   WebSocket notifications can trigger Telegram messages

This allows users to manage their AI workforce entirely from mobile.

------------------------------------------------------------------------

# Phase 7 --- GPT Codex Chat Interface

Terminal-style command system.

Examples:

    create agent named Researcher
    assign task: research AI startups
    show active agents

This allows fast interaction without UI.

------------------------------------------------------------------------

# Phase 8 --- Scheduling System

Agents can run scheduled jobs.

Example:

    TrendScout
    Schedule: every 2 hours
    Task: scan internet trends

Scheduler runs tasks automatically.

------------------------------------------------------------------------

# Phase 9 --- Tool Integrations

Agents will gain tools.

**Search Tools:**

-   Brave Search
-   Google Search

**Content Tools:**

-   Reddit API
-   YouTube API
-   Twitter API

**Development Tools:**

-   GitHub
-   Code execution

Agents call tools during tasks.

------------------------------------------------------------------------

# Phase 10 --- Scaling

Once core works:

-   allow 50+ agents
-   distributed workers
-   cloud deployment
-   persistent memory database

------------------------------------------------------------------------

# Minimum Viable Version

Version 1 should include only:

-   Create agent
-   Assign task
-   Parallel execution
-   Save outputs
-   Show agent status

No animation required initially.

------------------------------------------------------------------------

# Recommended Tech Stack

**Backend:** Python, FastAPI

**Concurrency:** asyncio

**AI Models:** OpenAI, Claude, local models (optional)

**UI:** Next.js, React

**Storage:** Local files (.md), SQLite (later upgrade)

**Messaging:** Telegram Bot API

------------------------------------------------------------------------

# Final Goal

Pulse AI becomes a **personal AI workforce system** where users manage a
team of autonomous agents running continuously to perform research,
coding, content creation, automation, and analysis.
