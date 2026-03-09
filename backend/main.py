from fastapi import FastAPI, HTTPException
from core.agent_manager import AgentManager
from core.output_manager import OutputManager
from core.orchestrator import Orchestrator
from pydantic import BaseModel
import asyncio

app = FastAPI(title="Pulse AI Backend")
agent_manager = AgentManager()
output_manager = OutputManager()
orchestrator = Orchestrator()

class CreateAgentRequest(BaseModel):
    name: str
    role: str
    model: str

class AssignTaskRequest(BaseModel):
    agent_id: str
    task: str

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(orchestrator.run())

@app.post("/agents")
def create_agent(request: CreateAgentRequest):
    agent = agent_manager.create_agent(request.name, request.role, request.model)
    return agent.dict()

@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: str):
    agent_manager.delete_agent(agent_id)
    return {"message": "Agent deleted"}

@app.post("/tasks")
def assign_task(request: AssignTaskRequest):
    agent_manager.assign_task(request.agent_id, request.task)
    return {"message": "Task assigned"}

@app.get("/agents")
def get_agents():
    return [agent.dict() for agent in agent_manager.get_agents()]

@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.dict()

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