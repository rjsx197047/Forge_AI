from typing import Dict, Any, Optional, Callable
from pydantic import BaseModel

class Tool(BaseModel):
    id: str
    name: str
    description: str
    params: Dict[str, Any] = {}

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.handlers: Dict[str, Callable] = {}

    def register_tool(self, tool_id: str, name: str, description: str, 
                     handler: Optional[Callable] = None):
        """Register a new tool"""
        tool = Tool(id=tool_id, name=name, description=description)
        self.tools[tool_id] = tool
        if handler:
            self.handlers[tool_id] = handler

    def list_tools(self) -> list[Tool]:
        """Get all registered tools"""
        return list(self.tools.values())

    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """Get a specific tool"""
        return self.tools.get(tool_id)

    async def execute_tool(self, tool_id: str, agent_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters"""
        if tool_id not in self.tools:
            return {"error": "Tool not found"}
        
        if tool_id in self.handlers:
            try:
                result = self.handlers[tool_id](agent_id=agent_id, **params)
                return {"success": True, "result": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Default echo tool behavior if no handler
        return {"success": True, "result": f"Tool {tool_id} executed with params: {params}"}
