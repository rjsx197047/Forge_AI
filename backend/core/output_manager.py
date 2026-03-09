import os
from typing import List, Dict
from datetime import datetime

class OutputManager:
    def __init__(self, outputs_dir: str = "outputs"):
        self.outputs_dir = outputs_dir
        os.makedirs(self.outputs_dir, exist_ok=True)

    def save_output(self, agent_name: str, task_id: str, content: str):
        agent_dir = os.path.join(self.outputs_dir, agent_name)
        os.makedirs(agent_dir, exist_ok=True)
        filename = f"task_{task_id}.md"
        filepath = os.path.join(agent_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)

    def get_outputs(self, agent_name: str = None) -> Dict[str, List[str]]:
        if agent_name:
            agent_dir = os.path.join(self.outputs_dir, agent_name)
            if os.path.exists(agent_dir):
                return {agent_name: os.listdir(agent_dir)}
            return {}
        else:
            result = {}
            for agent in os.listdir(self.outputs_dir):
                agent_dir = os.path.join(self.outputs_dir, agent)
                if os.path.isdir(agent_dir):
                    result[agent] = os.listdir(agent_dir)
            return result

    def get_output_content(self, agent_name: str, filename: str) -> str:
        filepath = os.path.join(self.outputs_dir, agent_name, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return f.read()
        return ""

    def delete_output(self, agent_name: str, filename: str):
        filepath = os.path.join(self.outputs_dir, agent_name, filename)
        if os.path.exists(filepath):
            os.remove(filepath)