from core.agent_manager import AgentManager
from core.output_manager import OutputManager
from core.ollama_integration import ollama_integration
import asyncio
import time
from datetime import datetime

class Orchestrator:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.output_manager = OutputManager()

    async def run_agent_worker(self, agent_id: str):
        agent = self.agent_manager.agents.get(agent_id)
        if not agent:
            return
        while True:
            if agent.task_queue:
                task = agent.task_queue.pop(0)
                agent.status = "working"
                self.agent_manager.save_agent(agent)
                
                # Execute task with Ollama AI
                try:
                    system_prompt = f"You are a {agent.role} assistant. Provide a detailed and helpful response."
                    response = await ollama_integration.generate_response(
                        model=agent.model,
                        prompt=task,
                        system_prompt=system_prompt,
                        temperature=0.7,
                        max_tokens=1024
                    )
                    
                    # Save output with Ollama response
                    content = f"# Task Report - {agent.name}\n\n## Task\n{task}\n\n## Response\n{response}\n\n## Metadata\n- Model: {agent.model}\n- Agent: {agent.name}\n- Role: {agent.role}\n- Completed: {datetime.now().isoformat()}"
                except Exception as e:
                    print(f"[Orchestrator] Error executing task with Ollama: {e}")
                    response = f"Error executing task with Ollama: {str(e)}"
                    content = f"# Task Report - {agent.name}\n\n## Task\n{task}\n\n## Error\n{response}\n\n## Metadata\n- Model: {agent.model}\n- Agent: {agent.name}\n- Completed: {datetime.now().isoformat()}"
                
                task_id = f"{int(time.time())}"
                self.output_manager.save_output(agent.name.lower(), task_id, content)
                agent.status = "idle"
                self.agent_manager.save_agent(agent)
            await asyncio.sleep(1)

    async def run(self):
        tasks = []
        for agent_id in self.agent_manager.agents:
            tasks.append(asyncio.create_task(self.run_agent_worker(agent_id)))
        await asyncio.gather(*tasks)