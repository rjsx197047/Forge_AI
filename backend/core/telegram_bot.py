import asyncio
import os
import json
from typing import Dict, List, Optional
from datetime import datetime

class TelegramBot:
    """
    Telegram bot interface for Pulse AI
    Handles commands like /agents, /task, /send_output, /outputs
    """
    def __init__(self, token: str, agent_manager, output_manager, websocket_manager=None):
        self.token = token
        self.agent_manager = agent_manager
        self.output_manager = output_manager
        self.websocket_manager = websocket_manager
        self.chat_sessions: Dict[str, Dict] = {}  # Track chat context
        self.command_handlers = {
            'start': self.handle_start,
            'agents': self.handle_agents,
            'task': self.handle_task,
            'outputs': self.handle_outputs,
            'send_output': self.handle_send_output,
            'status': self.handle_status,
            'help': self.handle_help,
        }
        print(f"[Telegram] Bot initialized with token: {token[:10]}...")

    async def run(self):
        """Run the Telegram bot polling (stub for production use with python-telegram-bot)"""
        while True:
            try:
                # In production, use:
                # await self.bot.get_updates()
                # This is where the actual polling/webhook handling would go
                await asyncio.sleep(10)
            except Exception as e:
                print(f"[Telegram] Error: {e}")
                await asyncio.sleep(5)

    async def handle_message(self, chat_id: str, message: str, user_id: str = None) -> str:
        """Handle incoming Telegram message and return response"""
        parts = message.strip().split(maxsplit=2)
        if not parts:
            return "No command received"
        
        command = parts[0].lstrip('/').lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.command_handlers:
            try:
                response = await self.command_handlers[command](chat_id, args, user_id)
                await self.send_message(chat_id, response)
                return response
            except Exception as e:
                error_msg = f"Error executing command: {str(e)}"
                await self.send_message(chat_id, error_msg)
                return error_msg
        else:
            return f"Unknown command: /{command}. Type /help for available commands."

    async def handle_start(self, chat_id: str, args: List[str], user_id: str = None) -> str:
        """Handle /start command"""
        self.chat_sessions[chat_id] = {
            'user_id': user_id,
            'connected_at': datetime.now().isoformat(),
            'command_count': 0
        }
        return """
Welcome to Pulse AI Mission Control 🤖

I can help you manage your AI agents remotely!

Use /help to see available commands or choose:
• /agents - List all agents
• /task [agent] [task] - Assign task to agent
• /outputs [agent] - Get agent's outputs
• /status [agent] - Check agent status
        """

    async def handle_agents(self, chat_id: str, args: List[str], user_id: str = None) -> str:
        """Handle /agents command - List all active agents"""
        agents = self.agent_manager.get_agents()
        
        if not agents:
            return "No agents found. Create an agent using the Mission Control UI."
        
        response = "📊 **Active Agents:**\n\n"
        for agent in agents:
            status_emoji = {
                'idle': '🟢',
                'working': '🔴',
                'thinking': '🟡',
                'complete': '🟣'
            }.get(agent.status, '⚪')
            
            response += f"{status_emoji} **{agent.name}** ({agent.role})\n"
            response += f"   ID: `{agent.id}`\n"
            response += f"   Status: {agent.status}\n"
            response += f"   Tasks queued: {len(agent.task_queue)}\n\n"
        
        return response.strip()

    async def handle_task(self, chat_id: str, args: List[str], user_id: str = None) -> str:
        """Handle /task command - Assign task to agent"""
        if len(args) < 2:
            return "Usage: /task [agent_id] [task_description]\nExample: /task researcher_01 Analyze market trends"
        
        agent_id = args[0]
        task_description = ' '.join(args[1:])
        
        agent = self.agent_manager.get_agent(agent_id)
        if not agent:
            return f"❌ Agent '{agent_id}' not found."
        
        self.agent_manager.assign_task(agent_id, task_description)
        
        if self.websocket_manager:
            await self.websocket_manager.broadcast({
                "event": "task_assigned",
                "agent_id": agent_id,
                "task": task_description,
                "timestamp": datetime.now().isoformat()
            })
        
        return f"""✅ Task assigned to {agent.name}!

📋 Task: {task_description}
👤 Agent: {agent.name} ({agent.role})
⏱️ Assigned at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The agent will return to the office and start working on this task.
Use /status {agent_id} to check progress.
        """

    async def handle_outputs(self, chat_id: str, args: List[str], user_id: str = None) -> str:
        """Handle /outputs command - List agent outputs"""
        agent_name = args[0] if args else None
        
        outputs = self.output_manager.get_outputs(agent_name)
        
        if not outputs:
            return "No outputs found."
        
        response = "📁 **Outputs:**\n\n"
        for agent, files in outputs.items():
            response += f"**{agent}**\n"
            if files:
                for file in files:
                    response += f"  • `{file}`\n"
            else:
                response += "  (No outputs yet)\n"
            response += "\n"
        
        return response.strip()

    async def handle_send_output(self, chat_id: str, args: List[str], user_id: str = None) -> str:
        """Handle /send_output command - Send specific output file"""
        if len(args) < 2:
            return "Usage: /send_output [agent_name] [filename]\nExample: /send_output researcher task_01_ai_startups.md"
        
        agent_name = args[0]
        filename = args[1]
        
        content = self.output_manager.get_output_content(agent_name, filename)
        if not content:
            return f"Output file not found: {agent_name}/{filename}"
        
        # If content is short, send as text message
        if len(content) < 4000:
            return f"📄 **{filename}** from {agent_name}:\n\n{content}"
        else:
            # In production, send as file attachment
            # For now, send truncated version
            return f"📄 **{filename}** from {agent_name}:\n\n{content[:3000]}...\n\n[Full file is {len(content)} bytes - view in Mission Control UI]"

    async def handle_status(self, chat_id: str, args: List[str], user_id: str = None) -> str:
        """Handle /status command - Check agent status"""
        if not args:
            return "Usage: /status [agent_id]\nExample: /status researcher_01"
        
        agent_id = args[0]
        agent = self.agent_manager.get_agent(agent_id)
        
        if not agent:
            return f"Agent '{agent_id}' not found."
        
        status_info = {
            'idle': '🟢 Idle - Waiting for tasks',
            'working': '🔴 Working - Task in progress',
            'thinking': '🟡 Thinking - Preparing',
            'complete': '🟣 Complete - Ready for next task'
        }
        
        response = f"""👤 **Agent Status Report**

Name: {agent.name}
Role: {agent.role}
Model: {agent.model}
Status: {status_info.get(agent.status, '⚪ Unknown')}

📚 Task Queue: {len(agent.task_queue)} tasks queued
Memory: {len(agent.memory)} bytes

Recent Tasks:
        """
        
        if agent.task_queue:
            for i, task in enumerate(agent.task_queue[:3], 1):
                response += f"{i}. {task}\n"
        else:
            response += "No active tasks"
        
        return response

    async def handle_help(self, chat_id: str, args: List[str], user_id: str = None) -> str:
        """Handle /help command"""
        return """
🤖 **Pulse AI Telegram Control**

Available Commands:

📊 **/agents** - List all active agents
   Shows: Name, Role, Status, Queued tasks

🎯 **/task [agent_id] [description]** - Assign task
   Example: /task researcher_01 Analyze market trends

📁 **/outputs [agent_id]** - List agent outputs
   Shows saved reports and files

📤 **/send_output [agent] [file]** - Get specific output
   Example: /send_output researcher task_01.md

📈 **/status [agent_id]** - Check agent status
   Shows detailed agent information

ℹ️ **/help** - Show this menu

💡 *Tips:*
• Use agent names from /agents command
• Tasks typically complete in 5-15 minutes
• Check outputs for generated reports
• All operations are logged and visible in Mission Control UI
        """

    async def send_message(self, chat_id: str, message: str):
        """Send message to Telegram chat (stub for production)"""
        print(f"[Telegram] Message to {chat_id}: {message[:50]}...")
        # In production, this would use:
        # await self.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

    async def send_notification(self, chat_id: str, title: str, message: str):
        """Send a formatted notification"""
        formatted = f"🔔 **{title}**\n\n{message}"
        await self.send_message(chat_id, formatted)

    async def broadcast_update(self, event_type: str, data: Dict):
        """Broadcast updates to all connected Telegram users"""
        if event_type == 'task_completed':
            message = f"""✅ **Task Completed!**
            
Agent: {data.get('agent_name')}
Duration: {data.get('duration')}
Output: {data.get('filename')}

Check /outputs to view the report.
            """
            # In production, send to all registered chat_ids
            print(f"[Telegram] Broadcasting: {event_type}")

    def get_session_info(self, chat_id: str) -> Dict:
        """Get Telegram chat session info"""
        return self.chat_sessions.get(chat_id, {})

