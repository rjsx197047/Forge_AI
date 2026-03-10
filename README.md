# Forge AI — Intelligent Agent Workforce Platform

![Forge AI Logo](https://img.shields.io/badge/Forge%20AI-Agent%20Platform-blue)
![Status](https://img.shields.io/badge/Status-Active%20Development-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **A comprehensive AI workforce management platform with real-time visualization, agent task orchestration, and Telegram integration — all wrapped in an intuitive "Pixel Office" interface.**

---

## Overview

Forge AI is a sophisticated platform for creating, managing, and visualizing autonomous AI agents. Instead of traditional dashboards, agents are represented as workers in a simulated office environment where their status and activity become immediately clear through visual metaphors.

**Key Capabilities:**
- Create and manage multiple AI agents with custom roles
- Real-time agent monitoring through interactive Dashboard
- Multi-room Pixel Office visualization with live agent animation
- Comprehensive Outputs manager for task reports and deliverables
- Task assignment and execution tracking
- Agent memory system with task history and statistics
- Telegram integration for remote agent control
- Dark mode support for comfortable viewing

---

## Project Structure

```
Forge_AI/
├── backend/                          # FastAPI backend server
│   ├── main.py                      # Application entry point
│   ├── requirements.txt              # Python dependencies
│   ├── core/                        # Core modules
│   │   ├── agent_manager.py        # Agent lifecycle and memory management
│   │   ├── orchestrator.py         # Task orchestration engine
│   │   ├── output_manager.py       # Output file handling
│   │   ├── scheduler.py            # Task scheduling
│   │   ├── telegram_bot.py         # Telegram command handler
│   │   ├── tool_manager.py         # Tool/capability management
│   │   └── websocket_manager.py    # Real-time WebSocket updates
│   ├── agents/                      # Agent configuration storage
│   ├── outputs/                     # Generated task outputs
│   ├── logs/                        # Application logs
│   ├── test_app.py                 # Basic testing
│   └── e2e_test.py                 # End-to-end test suite
│
├── frontend/                         # Next.js React frontend
│   ├── src/
│   │   ├── app/                    # Next.js app router
│   │   │   ├── page.tsx            # Mission Control main page
│   │   │   ├── layout.tsx          # Root layout with theme support
│   │   │   └── globals.css         # Global styles
│   │   ├── components/             # React components
│   │   │   ├── Dashboard.tsx       # Agent management dashboard
│   │   │   ├── Outputs.tsx         # Output file viewer
│   │   │   └── Office.tsx          # Pixel Office visualization
│   │   ├── lib/                    # Utility functions
│   │   │   └── api.ts              # Backend API client
│   │   └── types.ts                # TypeScript type definitions
│   ├── package.json                # Node dependencies
│   ├── tailwind.config.ts          # Tailwind CSS configuration
│   └── tsconfig.json               # TypeScript configuration
│
├── docs/
│   ├── Forge_AI_readme.md          # Main project specification
│   └── Forge_AI_advanced_pixel_office_readme.md  # Office visualization docs
│
└── README.md                        # This file
```

---

## Quick Start

### Prerequisites
- **Python 3.12+** with conda
- **Node.js 20+** with npm
- **Git** for version control

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn main:app --port 8000
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install JavaScript dependencies
npm install

# Start Next.js development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

---

## Usage

### Mission Control Dashboard

Access the complete UI at **http://localhost:3000**

#### Dashboard Tab
- **Create Agents** — Define new AI agents with custom roles
- **Assign Tasks** — Queue tasks for agents to execute
- **Monitor Status** — Track agent states (working, idle, thinking, complete)

#### Outputs Tab
- **Browse Reports** — View generated task outputs organized by agent
- **Read Content** — View rendered Markdown reports
- **Share to Telegram** — Send outputs to Telegram chat

#### Office Tab
- **Multi-Room Visualization** — 6-room office environment
- **Live Animation** — Watch agents move between rooms based on their status
- **Room Navigation** — See agent distribution per room
- **Agent Details** — Click any agent to view detailed information
- **Performance Metrics** — Toggle display of completion stats

#### Theme Toggle
- **Light Mode** — Clean, bright interface
- **Dark Mode** — Eye-friendly dark theme with persistent preference

---

## API Endpoints

### Agents
- `GET /agents` — List all agents
- `POST /agents` — Create new agent
- `GET /agents/{id}` — Get agent details
- `GET /agents/{id}/stats` — Get agent statistics with memory data

### Tasks
- `POST /tasks` — Assign task to agent
- `GET /tasks/{id}` — Get task details

### Outputs
- `GET /outputs` — List all outputs
- `GET /outputs/{agent_name}` — List outputs for specific agent
- `GET /outputs/{agent_name}/{filename}` — Get output content

### Telegram
- `POST /telegram/message` — Handle incoming Telegram messages
- `GET /telegram/agents` — Get agent list in Telegram format
- `GET /telegram/status` — Telegram connection status

### WebSocket
- `WS /ws/office` — Real-time office visualization updates

---

## Features

### Phase 1-3: Core Infrastructure ✅
- FastAPI backend with full REST API
- Agent lifecycle management
- Task execution and tracking
- Output file generation and storage
- Mission Control UI with Dashboard and Outputs tabs

### Phase 4-5: Visualization ✅
- Interactive Pixel Office with 6 rooms
- Real-time agent animation
- Room-based agent routing
- Performance metrics overlay
- Agent selection and detail panel
- Dark mode support

### Phase 6: Telegram Integration ✅
- `/agents` command — List active agents
- `/task [agent] [description]` — Assign tasks
- `/outputs [agent]` — List outputs
- `/send_output [agent] [task]` — Send report
- `/status` — System status
- `/help` — Command help

### Phase 7-8: Advanced (In Progress)
- Agent specialization and skill tracking
- Task scheduling and automation
- Agent collaboration indicators
- Advanced memory management

---

## Agent Memory System

Each agent maintains:
- **Task History** — Complete log of assigned and completed tasks
- **Statistics** — Success rates, average duration, completion count
- **Skills** — Proficiency profiles in specific domains
- **Specializations** — Domain expertise tracking

Data is automatically persisted to disk and recovered on restart.

---

## E2E Testing

Run the comprehensive test suite:

```bash
cd backend
python e2e_test.py
```

Tests include:
1. Health check endpoint
2. Agent creation and management
3. Task assignment and execution
4. Agent statistics retrieval
5. Output file generation
6. Telegram integration
7. Tool management
8. Complete workflow validation

---

## Configuration

### Environment Variables

```bash
# Backend
TELEGRAM_BOT_TOKEN=your_bot_token_here
PORT=8000
LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Agent Configuration

Agents are stored in `backend/agents/{agent_id}/config.json`:

```json
{
  "id": "researcher_01",
  "name": "Researcher",
  "role": "Market research specialist",
  "model": "gpt-4",
  "status": "idle",
  "task_queue": [],
  "memory_data": {
    "skills": [
      {"name": "research", "proficiency": 0.9}
    ],
    "task_history": [],
    "total_tasks_completed": 5,
    "avg_task_duration": 300,
    "success_rate": 0.95
  }
}
```

---

## Architecture

### Backend Stack
- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn 0.24.0
- **Validation:** Pydantic 2.5.0
- **Language:** Python 3.12
- **Real-time:** WebSocket support

### Frontend Stack
- **Framework:** Next.js 16.1.6
- **Library:** React 19
- **Language:** TypeScript 5
- **Styling:** TailwindCSS 4
- **Charts:** Chart.js for metrics

### Architecture Pattern
- **Communication:** REST API + WebSocket
- **State Management:** React hooks
- **Persistence:** File-based JSON storage
- **Real-time Updates:** Event-driven broadcasting

---

## Development Workflow

### Creating a New Feature

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** to backend or frontend

3. **Test your changes:**
   ```bash
   # Backend tests
   cd backend && python e2e_test.py
   
   # Frontend — verify in browser at http://localhost:3000
   ```

4. **Commit your changes:**
   ```bash
   git add -A
   git commit -m "feat: description of your feature"
   ```

5. **Push to GitHub:**
   ```bash
   git push origin feature/your-feature-name
   ```

---

## Troubleshooting

### Backend Won't Start
```bash
# Kill any process on port 8000
lsof -i :8000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# Restart backend
python -m uvicorn main:app --port 8000
```

### Frontend Won't Load
```bash
# Kill any process on port 3000
lsof -i :3000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# Clear Next.js cache and restart
rm -rf frontend/.next
cd frontend && npm run dev
```

### WebSocket Connection Issues
- Ensure backend is running on port 8000
- Check browser console for connection errors
- Verify CORS is enabled in FastAPI

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Submit a pull request with a description

---

## Roadmap

- [ ] **Phase 8:** Advanced task scheduling
- [ ] **Phase 9:** External API integrations (Google, OpenAI)
- [ ] **Phase 10:** Multi-user collaboration
- [ ] **Phase 11:** Cloud deployment (Azure, AWS)
- [ ] **Phase 12:** Advanced analytics and reporting

---

## License

MIT License — See [LICENSE](./LICENSE) file for details

---

## Support

For issues, questions, or suggestions:
- 📧 Email: support@forgeai.dev
- 🐛 Bug Reports: [GitHub Issues](https://github.com/yourusername/Forge_AI/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/Forge_AI/discussions)

---

## Acknowledgments

Built with modern tools using:
- FastAPI for robust backend architecture
- Next.js for modern frontend experience
- TailwindCSS for beautiful styling
- WebSocket for real-time updates

---

**Last Updated:** March 9, 2026  
**Status:** Active Development — Phase 5-6 Complete
