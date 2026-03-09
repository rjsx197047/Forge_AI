from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from pydantic import BaseModel

class Agent(BaseModel):
    id: str
    name: str
    role: str
    model: str
    status: str = "idle"
    task_queue: List[str] = []
    memory: str = ""

class AgentManager:
    def __init__(self, agents_dir: str = "agents"):
        self.agents_dir = agents_dir
        os.makedirs(self.agents_dir, exist_ok=True)
        self.agents: Dict[str, Agent] = {}
        self.load_agents()

    def load_agents(self):
        for agent_dir in os.listdir(self.agents_dir):
            config_path = os.path.join(self.agents_dir, agent_dir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    agent = Agent(**data)
                    self.agents[agent.id] = agent

    def save_agent(self, agent: Agent):
        agent_dir = os.path.join(self.agents_dir, agent.id)
        os.makedirs(agent_dir, exist_ok=True)
        config_path = os.path.join(agent_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump(agent.dict(), f, indent=2)

    def create_agent(self, name: str, role: str, model: str) -> Agent:
        agent_id = name.lower().replace(" ", "_")
        agent = Agent(id=agent_id, name=name, role=role, model=model)
        self.agents[agent_id] = agent
        self.save_agent(agent)
        return agent

    def delete_agent(self, agent_id: str):
        if agent_id in self.agents:
            del self.agents[agent_id]
            agent_dir = os.path.join(self.agents_dir, agent_id)
            if os.path.exists(agent_dir):
                import shutil
                shutil.rmtree(agent_dir)

    def assign_task(self, agent_id: str, task: str):
        if agent_id in self.agents:
            self.agents[agent_id].task_queue.append(task)
            self.save_agent(self.agents[agent_id])

    def get_agents(self) -> List[Agent]:
        return list(self.agents.values())

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.agents.get(agent_id)