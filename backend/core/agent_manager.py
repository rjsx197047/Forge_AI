from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from pydantic import BaseModel

class TaskHistory(BaseModel):
    task_id: str
    task_description: str
    status: str  # "pending", "working", "completed", "failed"
    started_at: str
    completed_at: Optional[str] = None
    duration_seconds: Optional[int] = None
    output_file: Optional[str] = None

class AgentMemory(BaseModel):
    skills: List[str] = []
    task_history: List[TaskHistory] = []
    total_tasks_completed: int = 0
    avg_task_duration: float = 0.0
    success_rate: float = 100.0
    specializations: Dict[str, float] = {}  # skill -> proficiency score

class Agent(BaseModel):
    id: str
    name: str
    role: str
    model: str
    status: str = "idle"
    task_queue: List[str] = []
    memory: str = ""
    created_at: str = ""
    last_activity: str = ""
    memory_data: AgentMemory = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.memory_data:
            self.memory_data = AgentMemory()

class AgentManager:
    def __init__(self, agents_dir: str = "agents"):
        self.agents_dir = agents_dir
        os.makedirs(self.agents_dir, exist_ok=True)
        self.agents: Dict[str, Agent] = {}
        self.load_agents()

    def load_agents(self):
        """Load all agents from disk"""
        if not os.path.exists(self.agents_dir):
            return
            
        for agent_dir in os.listdir(self.agents_dir):
            config_path = os.path.join(self.agents_dir, agent_dir, "config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        data = json.load(f)
                        # Reconstruct memory_data if it exists
                        if 'memory_data' in data and isinstance(data['memory_data'], dict):
                            data['memory_data'] = AgentMemory(**data['memory_data'])
                        agent = Agent(**data)
                        self.agents[agent.id] = agent
                        print(f"[Agent] Loaded agent: {agent.name} ({agent.id})")
                except Exception as e:
                    print(f"[Agent] Error loading {agent_dir}: {e}")

    def save_agent(self, agent: Agent):
        """Save agent to disk"""
        agent_dir = os.path.join(self.agents_dir, agent.id)
        os.makedirs(agent_dir, exist_ok=True)
        
        # Update last activity
        agent.last_activity = datetime.now().isoformat()
        
        config_path = os.path.join(agent_dir, "config.json")
        with open(config_path, 'w') as f:
            agent_data = agent.dict()
            # Convert memory_data back to dict for JSON serialization
            if agent.memory_data:
                agent_data['memory_data'] = agent.memory_data.dict()
            json.dump(agent_data, f, indent=2)

    def create_agent(self, name: str, role: str, model: str) -> Agent:
        """Create a new agent with Ollama AI"""
        agent_id = name.lower().replace(" ", "_")
        # Support for Ollama models: llama2, mistral, neural-chat, starling-lm, etc.
        if not model:
            model = "llama2"  # Default to Ollama's llama2
        agent = Agent(
            id=agent_id,
            name=name,
            role=role,
            model=model,
            created_at=datetime.now().isoformat(),
            memory_data=AgentMemory()
        )
        self.agents[agent_id] = agent
        self.save_agent(agent)
        return agent

    def delete_agent(self, agent_id: str):
        """Delete an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            agent_dir = os.path.join(self.agents_dir, agent_id)
            if os.path.exists(agent_dir):
                import shutil
                shutil.rmtree(agent_dir)
                print(f"[Agent] Deleted agent: {agent_id}")

    def assign_task(self, agent_id: str, task: str):
        """Assign task to agent"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.task_queue.append(task)
            
            # Add to task history
            task_history = TaskHistory(
                task_id=f"task_{len(agent.memory_data.task_history)}",
                task_description=task,
                status="pending",
                started_at=datetime.now().isoformat()
            )
            agent.memory_data.task_history.append(task_history)
            
            self.save_agent(agent)

    def complete_task(self, agent_id: str, task_index: int, duration_seconds: int, output_file: str = None):
        """Mark task as completed"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if task_index < len(agent.memory_data.task_history):
                task = agent.memory_data.task_history[task_index]
                task.status = "completed"
                task.completed_at = datetime.now().isoformat()
                task.duration_seconds = duration_seconds
                task.output_file = output_file
                
                # Update statistics
                agent.memory_data.total_tasks_completed += 1
                tasks = agent.memory_data.task_history
                completed_tasks = [t for t in tasks if t.status == "completed"]
                if completed_tasks:
                    total_duration = sum(t.duration_seconds for t in completed_tasks if t.duration_seconds)
                    agent.memory_data.avg_task_duration = total_duration / len(completed_tasks)
                
                self.save_agent(agent)

    def add_skill(self, agent_id: str, skill: str, proficiency: float = 1.0):
        """Add or update agent skill"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if skill not in agent.memory_data.skills:
                agent.memory_data.skills.append(skill)
            agent.memory_data.specializations[skill] = proficiency
            self.save_agent(agent)

    def get_agents(self) -> List[Agent]:
        """Get all agents"""
        return list(self.agents.values())

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get specific agent"""
        return self.agents.get(agent_id)

    def get_agent_memory(self, agent_id: str) -> Optional[AgentMemory]:
        """Get agent's memory data"""
        agent = self.agents.get(agent_id)
        if agent:
            return agent.memory_data
        return None

    def get_agent_stats(self, agent_id: str) -> Dict:
        """Get agent statistics"""
        agent = self.get_agent(agent_id)
        if not agent:
            return {}
        
        memory = agent.memory_data
        return {
            "id": agent.id,
            "name": agent.name,
            "role": agent.role,
            "status": agent.status,
            "created_at": agent.created_at,
            "last_activity": agent.last_activity,
            "total_tasks_completed": memory.total_tasks_completed,
            "avg_task_duration": memory.avg_task_duration,
            "success_rate": memory.success_rate,
            "skills": memory.skills,
            "specializations": memory.specializations
        }
