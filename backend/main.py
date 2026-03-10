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
from core.ollama_integration import OllamaIntegration
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
    print("Starting Forge AI Backend with Ollama AI...")
    
    # Check Ollama connection
    from core.ollama_integration import ollama_integration
    ollama_ready = await ollama_integration.check_connection()
    if ollama_ready:
        models = await ollama_integration.get_available_models()
        print(f"Ollama connected. Available models: {models}")
    else:
        print("Warning: Ollama not detected on localhost:11434. Please install and start Ollama.")
    
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
    
    print("Forge AI Backend startup complete")
    yield
    
    # Shutdown
    print("Shutting down Forge AI Backend")

# Initialize FastAPI with CORS and lifespan
app = FastAPI(title="Forge AI Backend - Powered by Ollama", lifespan=lifespan)
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

# ---- Ollama AI Endpoints ----
@app.get("/ollama/models")
async def get_ollama_models():
    """Get list of available Ollama models"""
    models = await ollama_integration.get_available_models()
    return {
        "models": models,
        "status": "connected" if models else "disconnected",
        "message": "Ollama AI models available" if models else "Ollama not responding. Install from https://ollama.ai"
    }

@app.get("/ollama/status")
async def get_ollama_status():
    """Check Ollama connection status"""
    is_connected = await ollama_integration.check_connection()
    models = await ollama_integration.get_available_models() if is_connected else []
    return {
        "connected": is_connected,
        "models": models,
        "endpoint": ollama_integration.base_url
    }

# ---- Task Endpoints ----
@app.post("/tasks")
def assign_task(request: AssignTaskRequest):
    """Assign a task to an agent"""
    try:
        agent = agent_manager.get_agent(request.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{request.agent_id}' not found")
        
        agent_manager.assign_task(request.agent_id, request.task)
        asyncio.create_task(websocket_manager.broadcast({
            "event": "task_assigned",
            "agent_id": request.agent_id,
            "task": request.task
        }))
        return {"message": "Task assigned", "agent_id": request.agent_id, "task": request.task}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Tasks] Error assigning task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assign task: {str(e)}")

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

# ---- Agent Stats Endpoint ----
@app.get("/agents/{agent_id}/stats")
def get_agent_stats(agent_id: str):
    stats = agent_manager.get_agent_stats(agent_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Agent not found")
    return stats

# ---- Telegram Endpoints ----
class TelegramMessage(BaseModel):
    chat_id: str
    message: str
    user_id: str = None

@app.post("/telegram/message")
async def handle_telegram_message(request: TelegramMessage):
    """Handle incoming Telegram messages"""
    global telegram_bot
    
    if not telegram_bot:
        # Initialize Telegram bot if not already done
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if telegram_token:
            telegram_bot = TelegramBot(telegram_token, agent_manager, output_manager, websocket_manager)
        else:
            raise HTTPException(status_code=400, detail="Telegram bot not configured")
    
    try:
        response = await telegram_bot.handle_message(
            request.chat_id,
            request.message,
            request.user_id
        )
        return {"success": True, "response": response}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/telegram/agents")
def telegram_get_agents():
    """API endpoint for Telegram to fetch agent list"""
    agents = agent_manager.get_agents()
    return {
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "role": a.role,
                "status": a.status,
                "tasks_queued": len(a.task_queue)
            }
            for a in agents
        ]
    }

@app.get("/telegram/status")
def health_check():
    return {
        "status": "healthy",
        "agents_count": len(agent_manager.get_agents()),
        "outputs_count": len(output_manager.get_outputs()),
        "telegram_connected": telegram_bot is not None
    }