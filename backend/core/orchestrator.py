from core.agent_manager import AgentManager
from core.output_manager import OutputManager
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
                # Simulate task execution
                await asyncio.sleep(5)  # Simulate work
                # Save output
                content = f"# Task Report\n\nTask: {task}\n\nCompleted at {datetime.now()}\n\n[Simulated output]"
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