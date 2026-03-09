import asyncio
from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel

class Schedule(BaseModel):
    id: str
    agent_id: str
    task: str
    interval_seconds: int
    created_at: str

class Scheduler:
    def __init__(self):
        self.schedules: Dict[str, Schedule] = {}
        self.next_id = 0

    def create_schedule(self, agent_id: str, task: str, interval_seconds: int) -> Schedule:
        schedule_id = f"sched_{self.next_id}"
        self.next_id += 1
        schedule = Schedule(
            id=schedule_id,
            agent_id=agent_id,
            task=task,
            interval_seconds=interval_seconds,
            created_at=datetime.now().isoformat()
        )
        self.schedules[schedule_id] = schedule
        return schedule

    def delete_schedule(self, schedule_id: str):
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]

    def list_schedules(self):
        return list(self.schedules.values())

    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        return self.schedules.get(schedule_id)

    async def run(self, agent_manager, websocket_manager):
        """Background task that executes scheduled tasks"""
        while True:
            for schedule_id, schedule in list(self.schedules.items()):
                # Assign task to agent
                if agent_manager.get_agent(schedule.agent_id):
                    agent_manager.assign_task(schedule.agent_id, schedule.task)
                    await websocket_manager.broadcast({
                        "event": "task_scheduled",
                        "schedule_id": schedule_id,
                        "agent_id": schedule.agent_id,
                        "task": schedule.task,
                        "timestamp": datetime.now().isoformat()
                    })
                await asyncio.sleep(schedule.interval_seconds)
