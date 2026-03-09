from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.agent_manager import AgentManager
from core.output_manager import OutputManager
import asyncio

app = FastAPI(title="Pulse AI Backend - Test")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_manager = AgentManager()
output_manager = OutputManager()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "agents": len(agent_manager.get_agents()),
        "outputs": len(output_manager.get_outputs())
    }

@app.get("/agents")
def get_agents():
    return [agent.dict() for agent in agent_manager.get_agents()]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
