# Pulse AI --- Advanced Pixel Office Technical Specification

## Document Purpose

This document provides the **detailed technical specification** for the Pulse AI Pixel Office visualization system --- an animated interface where AI agents are represented as workers in a virtual office environment.

> **Related Documentation:** This is the advanced technical reference for **Phase 5 (Office Visualization)** described in the [main Pulse AI roadmap](./Forge_AI_readme.md). Read the main roadmap first for platform context.

## Overview

The Pixel Office transforms traditional agent monitoring into an intuitive visual experience where:

-   Agents exist as **worker sprites** in a simulated office space
-   Movement and position indicate **agent state and activity**
-   **Real-time updates** show task progress and completion
-   Multiple agents operate **simultaneously** with live visualization
-   State changes trigger **animated transitions**

**Key Principle:** Visual metaphors replace text-heavy dashboards --- users understand agent status at a glance.

------------------------------------------------------------------------

# Core Concept

Instead of a normal dashboard, agents live inside a **visual office
simulation**.

Agent states:

  State      Behavior
  ---------- -----------------------
  Idle       Wanders around office
  Thinking   Stands near desk
  Working    Moves to desk
  Complete   Returns to lounge

------------------------------------------------------------------------

# System Architecture

## Integration with Pulse AI Platform

The Pixel Office is the **visual layer** of the Pulse AI platform. It sits on top of the core backend architecture described in the [main roadmap](./Forge_AI_readme.md):

    ┌─────────────────────────────────────────┐
    │         User Interface Layer            │
    │                                         │
    │  Mission Control Tabs:                  │
    │   - Dashboard (Phase 3)                 │
    │   - Outputs (Phase 3)                   │
    │   - Pixel Office (Phase 5) ◄── THIS DOC │
    │                                         │
    └────────────────┬────────────────────────┘
                     │ HTTP / WebSocket
    ┌────────────────┴────────────────────────┐
    │    Pulse Core Backend (FastAPI)         │
    │                                         │
    │  Agent Manager API                      │
    │   - create_agent()                      │
    │   - assign_task()                       │
    │   - get_agent_status()                  │
    │                                         │
    │  Outputs Manager                        │
    │   - save_output()                       │
    │   - list_outputs()                      │
    │                                         │
    │  Telegram Interface                     │
    │   - send_notification()                 │
    │   - handle_commands()                   │
    │                                         │
    └────────────────┬────────────────────────┘
                     │
    ┌────────────────┴────────────────────────┐
    │         Agent Worker Layer              │
    │  - Parallel async workers               │
    │  - Task execution                       │
    │  - State broadcasting                   │
    └─────────────────────────────────────────┘

## Data Flow

### WebSocket Approach (Recommended)

    ws://localhost:8000/ws/office

    // Backend broadcasts on state change:
    {
      "event": "agent_state_update",
      "agent_id": "researcher_01",
      "state": "working",
      "desk_id": 1,
      "position": {"x": 150, "y": 100},
      "current_task": "Analyzing AI startup trends",
      "task_progress": 45,
      "timestamp": "2026-03-09T10:30:00Z"
    }

### Polling Approach (Simpler)

    GET /agents/status     # Poll every 2-3 seconds

    {
      "agents": [
        {
          "id": "researcher_01",
          "name": "Jarvis",
          "state": "working",
          "desk_id": 1,
          "current_task": "Analyzing AI startup trends"
        },
        {
          "id": "coder_01",
          "name": "Atlas",
          "state": "thinking",
          "desk_id": 2,
          "current_task": "Implementing feature X"
        }
      ],
      "timestamp": "2026-03-09T10:30:00Z"
    }

## Event Types

The backend emits these events that the Pixel Office consumes:

1.  **`agent_created`** --- New agent added, spawn sprite in idle area
2.  **`agent_deleted`** --- Remove agent sprite from office
3.  **`task_assigned`** --- Agent moves to "thinking" state
4.  **`task_started`** --- Agent moves to desk, "working" state
5.  **`task_completed`** --- Agent returns to idle, triggers output notification
6.  **`agent_idle`** --- Agent wanders in common area
7.  **`output_saved`** --- Report saved, notification in Pixel Office
8.  **`telegram_delivery`** --- Visual indicator of output sent to Telegram

## FastAPI WebSocket Endpoint Example

``` python
# core/websocket_manager.py

from fastapi import WebSocket
from typing import List

class OfficeWebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def broadcast_agent_update(self, agent_data: dict):
        for connection in self.active_connections:
            await connection.send_json({
                "event": "agent_state_update",
                **agent_data
            })

# main.py
@app.websocket("/ws/office")
async def office_websocket(websocket: WebSocket):
    await office_manager.connect(websocket)
    # Keep connection alive and send updates
```

------------------------------------------------------------------------

# Pixel Office Prototype (Reference Implementation)

The following HTML/JS demo serves as a **functional prototype and reference implementation** for the Pixel Office visualization system.

**Purpose:**

-   Demonstrate core concepts (agent sprites, desks, state transitions)
-   Provide visual reference for the production implementation
-   Test animation timing and user experience
-   Serve as proof-of-concept for stakeholder demos

Save this code as `office_prototype.html` and open in a browser.

**Note:** This is a standalone prototype. The production version will be built in React/Next.js with real backend integration (see System Architecture above).

## Prototype Features

This demo includes:

• animated workers\
• desks\
• walking movement\
• live agent state simulation\
• ability to add agents

``` html
<!DOCTYPE html>
<html>
<head>

<title>Pulse AI Office</title>

<style>

body{
background:#0f172a;
color:white;
font-family:sans-serif;
text-align:center;
}

.office{
position:relative;
width:900px;
height:550px;
margin:auto;
background:#1e293b;
border-radius:12px;
overflow:hidden;
}

.grid{
position:absolute;
width:100%;
height:100%;
background-image:linear-gradient(#233048 1px, transparent 1px),
linear-gradient(90deg,#233048 1px, transparent 1px);
background-size:40px 40px;
opacity:0.3;
}

.desk{
position:absolute;
width:120px;
height:60px;
background:#334155;
border-radius:6px;
}

.worker{
position:absolute;
width:18px;
height:18px;
background:#22c55e;
border-radius:2px;
transition:all 1s linear;
}

.idle{background:#ef4444}
.thinking{background:#f59e0b}
.working{background:#22c55e}

.controls{
margin:20px;
}

button{
padding:10px 15px;
border:none;
border-radius:6px;
background:#3b82f6;
color:white;
cursor:pointer;
}

</style>

</head>

<body>

<h2>Pulse AI Pixel Headquarters</h2>

<div class="controls">
<button onclick="addAgent()">Add Agent</button>
<button onclick="assignTasks()">Assign Random Tasks</button>
</div>

<div class="office">

<div class="grid"></div>

<div class="desk" style="top:120px;left:150px"></div>
<div class="desk" style="top:120px;left:380px"></div>
<div class="desk" style="top:120px;left:610px"></div>

</div>

<script>

let agents=[]
let office=document.querySelector(".office")

function createWorker(id){

let w=document.createElement("div")
w.className="worker idle"
w.id=id

w.style.left=Math.random()*800+"px"
w.style.top="420px"

office.appendChild(w)

}

function addAgent(){

let id="agent"+agents.length

agents.push({
id:id,
state:"idle",
desk:Math.floor(Math.random()*3)
})

createWorker(id)

}

function assignTasks(){

agents.forEach(a=>{

let states=["idle","thinking","working"]
a.state=states[Math.floor(Math.random()*states.length)]

let el=document.getElementById(a.id)

el.className="worker "+a.state

if(a.state==="working"){

let desks=[150,380,610]

el.style.left=desks[a.desk]+"px"
el.style.top="100px"

}

else if(a.state==="thinking"){

let desks=[150,380,610]

el.style.left=desks[a.desk]+"px"
el.style.top="70px"

}

else{

el.style.top="420px"
el.style.left=Math.random()*800+"px"

}

})

}

setInterval(assignTasks,4000)

</script>

</body>
</html>
```

------------------------------------------------------------------------

# Features

This prototype demonstrates:

• Multiple agents running simultaneously\
• Dynamic agent creation\
• Task assignment simulation\
• Desk-based working system\
• Movement animations\
• Office grid environment

------------------------------------------------------------------------

# Planned Advanced Features

Beyond the MVP implementation, future versions can include the following. Many of these connect to other phases in the [main Pulse AI roadmap](./Forge_AI_readme.md).

### Real Agent Backend (Integrated)

Connect the UI to:

-   OpenAI Agents
-   Local LLM workers
-   Docker containers

### WebSocket Updates

Agents update in real time:

    agent.status = "working"
    agent.location = desk_3

### Walking Animations

Sprite-based movement:

-   walking left/right
-   sitting at desk
-   going to kitchen

### Office Rooms

Add areas:

-   meeting room
-   gym
-   kitchen
-   brainstorming room

### Agent Memory

Each worker maintains:

-   task history
-   memory vector store
-   skill specialization

### Multi-Room Office

Expand beyond single office view:

-   **Main Office** --- Standard work desks
-   **Meeting Room** --- When agents collaborate on tasks
-   **Research Library** --- For research-focused agents
-   **Code Lab** --- For development agents
-   **Delivery Hub** --- Telegram and output management zone
-   **Break Room** --- Idle agents gather here

Users can navigate between rooms to see specialized activities.

### Agent Collaboration Indicators

Show when agents work together:

-   Two agents move to meeting room
-   Shared task indicator above both
-   Lines connecting collaborating agents
-   Combined output in Outputs tab

### Performance Metrics Overlay

Toggle-able overlay showing:

-   Tasks completed per agent (last 24h)
-   Average task duration
-   Success/failure rates
-   Output generation trends

### Customization

Allow users to personalize the office:

-   Upload custom sprite images
-   Configure office layout
-   Choose color themes
-   Add custom rooms/zones

------------------------------------------------------------------------

# Outputs Tab Integration

The Pixel Office visually represents when agents generate outputs, which are then accessible via the **Outputs tab** (see [Phase 3 in the main roadmap](./Forge_AI_readme.md)).

## Visual Output Indicators

### Completion Animation

When an agent completes a task and saves a `.md` report:

1.  Agent sprite changes to "complete" state (blue)
2.  Small document icon appears above agent
3.  Agent "walks" toward a delivery zone
4.  Output counter increments in UI corner

### Output Notification Banner

Upon task completion, a notification slides in:

    ┌────────────────────────────────────────┐
    │  Researcher completed task             │
    │  Report: "AI Startup Analysis"         │
    │  [View in Outputs Tab] [Send to Telegram] │
    └────────────────────────────────────────┘

### Agent Info Panel

Clicking an agent sprite shows:

    Agent: Researcher (Jarvis)
    Status: Complete
    ━━━━━━━━━━━━━━━━━━━━━━
    Recent Output:
    task_01_ai_startups.md
       Completed: 2 min ago
       Size: 4.2 KB

    [View Report] [Details]

## Outputs Tab Features

The Outputs tab provides comprehensive report management (see [main roadmap Phase 3](./Forge_AI_readme.md) for full specification).

**Browse by Agent:**

-   Organized folder structure
-   Reports grouped by agent name
-   Sorted by completion time

**Report Viewer:**

-   Click any .md file to view rendered Markdown
-   Syntax highlighting
-   Full-width reading experience

**Search & Filter:**

-   Search within report content
-   Filter by agent, date, keywords
-   Sort options

**Quick Actions:**

-   Download .md file
-   Copy to clipboard
-   **Share via Telegram** (integration with Phase 6)
-   Delete output

## Data Storage Structure

    outputs/
    ├─ researcher/
    │  ├─ task_01_ai_startups.md
    │  ├─ task_02_competitor_analysis.md
    │  └─ task_03_market_trends.md
    ├─ coder/
    │  ├─ task_01_feature_implementation.md
    │  └─ task_02_bug_fixes.md
    └─ writer/
       ├─ task_01_blog_post.md
       └─ task_02_documentation.md

Each `.md` file contains:

    # Task Report: AI Startup Analysis

    **Agent:** Researcher (Jarvis)
    **Completed:** 2026-03-09 10:30:00
    **Duration:** 12 minutes

    ## Summary
    [Agent-generated content...]

    ## Findings
    1. Company A - Series B, $50M funding
    2. Company B - Seed stage, $3M funding

## Backend API for Outputs

REST Endpoints:

    GET    /outputs                       # All outputs across all agents
    GET    /outputs/{agent_name}          # Outputs for specific agent
    GET    /outputs/{agent_name}/{task_id} # Specific output file
    POST   /outputs/{agent_name}          # Agent saves new output (internal)
    DELETE /outputs/{agent_name}/{task_id} # Delete output (user action)

WebSocket event when output is saved:

    {
      "event": "output_saved",
      "agent_id": "researcher_01",
      "agent_name": "Researcher",
      "task_id": "task_01",
      "filename": "task_01_ai_startups.md",
      "file_size": 4231,
      "timestamp": "2026-03-09T10:30:00Z"
    }

This event triggers:

1.  **Pixel Office:** Show completion animation
2.  **Outputs Tab:** Refresh file list
3.  **Telegram:** Send notification (if configured)

## User Flow Example

1.  User assigns task via Mission Control: "Research AI startups"
2.  **Pixel Office** shows agent moving to desk (working state)
3.  Agent processes task
4.  Agent completes and calls `save_output()`
5.  **Backend** saves `outputs/researcher/task_01_ai_startups.md`
6.  **WebSocket** broadcasts `output_saved` event
7.  **Pixel Office** shows completion animation
8.  **Outputs Tab** updates with new file
9.  **Telegram** (if enabled) sends notification
10. User clicks "View in Outputs Tab" to read the rendered report

------------------------------------------------------------------------

# Telegram Delivery Integration

The Pixel Office integrates with **Phase 6 (Telegram Interface)** from the [main roadmap](./Forge_AI_readme.md) to enable mobile-first output delivery and remote agent control.

## Visual Telegram Indicators

### Delivery Zone

The office layout includes a **Telegram Delivery Zone**:

    ┌─────────────────────────────────┐
    │      Office Layout              │
    │                                 │
    │  [Desk] [Desk] [Desk]          │
    │                                 │
    │  [Common Area - Idle Agents]    │
    │                                 │
    │  [Telegram Delivery Zone]       │
    └─────────────────────────────────┘

When an agent completes a task configured for Telegram delivery:

1.  Agent turns "complete" blue
2.  Agent "walks" to Telegram Delivery Zone
3.  Animation shows output being "sent"
4.  Agent returns to idle state

### Telegram Status Indicator

Top-right corner shows Telegram connection status (Connected / Disconnected).

## Telegram Commands Integration

Users can control the Pixel Office via Telegram:

### Agent Management

    /agents

    Response:
    Researcher - Working on "AI Analysis"
    Coder - Idle
    Writer - Thinking

### Task Assignment

    /task researcher Find trending AI topics

    Response:
    Task assigned to Researcher
    Agent moving to desk
    Estimated time: 10 min

### Output Delivery

**Automatic Notifications:**

When agent completes task:

    Researcher completed: "AI Startup Analysis"

    Results:
    - Duration: 12 minutes
    - Output size: 4.2 KB

    Report saved to Outputs tab

    Commands:
    /send_output researcher task_01 — Send full report
    /outputs researcher — List all Researcher outputs

**Manual Retrieval:**

    /send_output researcher task_01

    Response: [Full report sent as file attachment if >2000 chars]

## Agent Telegram Config

Agents can have Telegram delivery settings:

    {
      "name": "Researcher",
      "role": "Market research",
      "telegram": {
        "auto_notify": true,
        "delivery_mode": "notification_only",
        "notify_on": ["task_complete", "error"],
        "chat_id": "123456789"
      }
    }

Delivery modes:

-   `notification_only` --- Just sends completion notification
-   `full_report` --- Sends report content in message (if <2000 chars)
-   `file_attachment` --- Always sends .md file

## Desktop + Mobile Workflow

1.  **Desktop:** User assigns task in Mission Control UI
2.  **Desktop:** Pixel Office shows agent working
3.  **Mobile:** Telegram notification: "Agent working on task..."
4.  User leaves computer
5.  **Mobile:** Telegram notification: "Task complete!"
6.  **Mobile:** User types `/send_output researcher task_01`
7.  **Mobile:** Receives full .md report as file
8.  **Desktop (later):** User opens Outputs tab to review in web UI

------------------------------------------------------------------------

# End Goal

The Pixel Office transforms traditional agent monitoring into an **intuitive, living workspace** where:

-   **Visual metaphors** replace complex status tables
-   **Real-time animations** provide immediate feedback
-   **Integrated workflows** connect visualization, outputs, and Telegram delivery
-   **Scalability** supports 10-50+ concurrent agents without performance degradation

**Vision:** A user opens Pulse AI and sees their digital workforce as a thriving office --- agents moving, working, and delivering results --- all in an interface that feels alive and responsive.

The Pixel Office is **one component** of the complete Pulse AI platform (see [main roadmap](./Forge_AI_readme.md)), working alongside:

-   **Mission Control** (Phase 3) --- Dashboard and Outputs browser
-   **Agent Creation UI** (Phase 4) --- Dynamic agent configuration
-   **Telegram Interface** (Phase 6) --- Mobile-first control and delivery
-   **Scheduling** (Phase 8) --- Automated task management
-   **Tool Integrations** (Phase 9) --- External API capabilities

Together, these components create a **comprehensive AI workforce platform** where the Pixel Office provides the visual heart of the system.
