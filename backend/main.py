from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.agent_manager import AgentManager
from core.output_manager import OutputManager
from core.orchestrator import Orchestrator
from core.websocket_manager import websocket_manager
from core.telegram_bot import TelegramBot
from core.scheduler import Scheduler
from core.tool_manager import ToolManager
from pydantic import BaseModel
import asyncio
import os

# Initialize core components
agent_manager = AgentManager()
output_manager = OutputManager()
orchestrator = Orchestrator()
tool_manager = ToolManager()
scheduler = None
telegram_bot = None

# Register sample tools
tool_manager.register_tool("echo", "Echo Tool", "Returns back provided parameters")

class CreateAgentRequest(BaseModel):
    name: str
    role: str
    model: str

class AssignTaskRequest(BaseModel):
    agent_id: str
    task: str

class ScheduleRequest(BaseModel):
    agent_id: str
    task: str
    interval_seconds: int

class ToolRequest(BaseModel):
    tool_id: str
    agent_id: str
    params: dict = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global scheduler, telegram_bot
    print("Starting Pulse AI Backend...")
    
    try:
        asyncio.create_task(orchestrator.run())
        print("Orchestrator task created")
    except Exception as e:
        print(f"Error creating orchestrator task: {e}")
    
    # Initialize scheduler (commented out for now)
    # scheduler = Scheduler()
    # asyncio.create_task(scheduler.run(agent_manager, websocket_manager))
    
    # Initialize Telegram bot if token provided (commented out for now)
    # telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    # if telegram_token:
    #     telegram_bot = TelegramBot(telegram_token, agent_manager, output_manager)
    #     asyncio.create_task(telegram_bot.run())
    
    print("Pulse AI Backend startup complete")
    yield
    
    # Shutdown
    print("Shutting down Pulse AI Backend")

# Initialize FastAPI with CORS and lifespan
app = FastAPI(title="Pulse AI Backend", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint for office visualization
@app.websocket("/ws/office")
async def office_websocket(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except Exception:
        websocket_manager.disconnect(websocket)

# ---- Agent Endpoints ----
@app.post("/agents")
def create_agent(request: CreateAgentRequest):
    agent = agent_manager.create_agent(request.name, request.role, request.model)
    asyncio.create_task(websocket_manager.broadcast({
        "event": "agent_created",
        "agent": agent.dict()
    }))
    return agent.dict()

@app.get("/agents")
def get_agents():
    return [agent.dict() for agent in agent_manager.get_agents()]

@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.dict()

@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: str):
    agent_manager.delete_agent(agent_id)
    asyncio.create_task(websocket_manager.broadcast({
        "event": "agent_deleted",
        "agent_id": agent_id
    }))
    return {"message": "Agent deleted"}

# ---- Task Endpoints ----
@app.post("/tasks")
def assign_task(request: AssignTaskRequest):
    agent_manager.assign_task(request.agent_id, request.task)
    asyncio.create_task(websocket_manager.broadcast({
        "event": "task_assigned",
        "agent_id": request.agent_id,
        "task": request.task
    }))
    return {"message": "Task assigned"}

# ---- Schedule Endpoints ----
@app.post("/schedules")
def create_schedule(request: ScheduleRequest):
    if not scheduler:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")
    sched = scheduler.create_schedule(request.agent_id, request.task, request.interval_seconds)
    return sched.dict()

@app.get("/schedules")
def list_schedules():
    if not scheduler:
        return []
    return [sched.dict() for sched in scheduler.list_schedules()]

@app.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: str):
    if not scheduler:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")
    scheduler.delete_schedule(schedule_id)
    return {"message": "Schedule deleted"}

# ---- Output Endpoints ----
@app.get("/outputs")
def get_outputs(agent_name: str = None):
    return output_manager.get_outputs(agent_name)

@app.get("/outputs/{agent_name}/{filename}")
def get_output(agent_name: str, filename: str):
    content = output_manager.get_output_content(agent_name, filename)
    if not content:
        raise HTTPException(status_code=404, detail="Output not found")
    return {"content": content}

@app.delete("/outputs/{agent_name}/{filename}")
def delete_output(agent_name: str, filename: str):
    output_manager.delete_output(agent_name, filename)
    return {"message": "Output deleted"}

# ---- Tool Endpoints ----
@app.get("/tools")
def list_tools():
    return [tool.dict() for tool in tool_manager.list_tools()]

@app.post("/tools/execute")
async def execute_tool(request: ToolRequest):
    result = await tool_manager.execute_tool(request.tool_id, request.agent_id, request.params)
    return result

# ---- Health Check ----
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "agents": len(agent_manager.get_agents()),
        "outputs": len(output_manager.get_outputs())
    }