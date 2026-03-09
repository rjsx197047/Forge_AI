#!/usr/bin/env python3
"""
End-to-End Integration Test for Pulse AI
Tests the complete workflow: Create agents → Assign tasks → Check outputs
"""

import asyncio
import json
import sys
import time
from datetime import datetime

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    print(f"{YELLOW}ℹ{RESET} {msg}")

class E2ETestSuite:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.agents = []
        self.tasks_assigned = []
        
    async def test_health(self):
        """Test 1: Health check endpoint"""
        print_section("Test 1: Health Check")
        try:
            import urllib.request
            response = urllib.request.urlopen(f"{self.base_url}/health")
            data = json.loads(response.read().decode())
            print_success(f"Backend is healthy")
            print_info(f"  Status: {data['status']}")
            print_info(f"  Agents: {data['agents']}")
            print_info(f"  Outputs: {data['outputs']}")
            return True
        except Exception as e:
            print_error(f"Health check failed: {e}")
            return False

    async def test_create_agents(self):
        """Test 2: Create multiple agents"""
        print_section("Test 2: Create Agents")
        
        test_agents = [
            {"name": "Researcher", "role": "Market Research", "model": "gpt-4"},
            {"name": "Developer", "role": "Code Generation", "model": "gpt-4"},
            {"name": "Writer", "role": "Content Creation", "model": "gpt-3.5"},
        ]
        
        try:
            import urllib.request
            for agent_data in test_agents:
                url = f"{self.base_url}/agents"
                payload = json.dumps(agent_data).encode()
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                response = urllib.request.urlopen(req)
                agent = json.loads(response.read().decode())
                self.agents.append(agent)
                print_success(f"Created agent: {agent['name']} ({agent['id']})")
            return True
        except Exception as e:
            print_error(f"Failed to create agents: {e}")
            return False

    async def test_list_agents(self):
        """Test 3: List all agents"""
        print_section("Test 3: List Agents")
        
        try:
            import urllib.request
            response = urllib.request.urlopen(f"{self.base_url}/agents")
            agents = json.loads(response.read().decode())
            print_success(f"Retrieved {len(agents)} agents")
            for agent in agents:
                print_info(f"  - {agent['name']}: {agent['status']}")
            return len(agents) > 0
        except Exception as e:
            print_error(f"Failed to list agents: {e}")
            return False

    async def test_assign_tasks(self):
        """Test 4: Assign tasks to agents"""
        print_section("Test 4: Assign Tasks")
        
        if not self.agents:
            print_error("No agents available to assign tasks")
            return False
        
        tasks = [
            {"agent_id": self.agents[0]['id'], "task": "Analyze market trends for AI startups"},
            {"agent_id": self.agents[1]['id'], "task": "Write a Python script for data processing"},
            {"agent_id": self.agents[2]['id'], "task": "Create a blog post about machine learning"},
        ]
        
        try:
            import urllib.request
            for task_data in tasks:
                url = f"{self.base_url}/tasks"
                payload = json.dumps(task_data).encode()
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                response = urllib.request.urlopen(req)
                result = json.loads(response.read().decode())
                self.tasks_assigned.append(task_data)
                print_success(f"Assigned task to {task_data['agent_id']}")
                print_info(f"  Task: {task_data['task'][:50]}...")
            return True
        except Exception as e:
            print_error(f"Failed to assign tasks: {e}")
            return False

    async def test_get_agent_stats(self):
        """Test 5: Get agent statistics"""
        print_section("Test 5: Agent Statistics")
        
        if not self.agents:
            print_error("No agents available")
            return False
        
        try:
            import urllib.request
            for agent in self.agents:
                url = f"{self.base_url}/agents/{agent['id']}/stats"
                response = urllib.request.urlopen(url)
                stats = json.loads(response.read().decode())
                print_success(f"Stats for {agent['name']}:")
                print_info(f"  Status: {stats['status']}")
                print_info(f"  Created: {stats['created_at']}")
                print_info(f"  Tasks Completed: {stats['total_tasks_completed']}")
                print_info(f"  Skills: {', '.join(stats['skills']) if stats['skills'] else 'None'}")
            return True
        except Exception as e:
            print_error(f"Failed to get stats: {e}")
            return False

    async def test_outputs(self):
        """Test 6: Check outputs"""
        print_section("Test 6: Outputs")
        
        try:
            import urllib.request
            response = urllib.request.urlopen(f"{self.base_url}/outputs")
            outputs = json.loads(response.read().decode())
            
            if outputs:
                print_success(f"Found outputs:")
                for agent_name, files in outputs.items():
                    print_info(f"  {agent_name}: {len(files)} files")
                    for file in files[:3]:  # Show first 3
                        print_info(f"    - {file}")
            else:
                print_info("No outputs generated yet (agents still working)")
            return True
        except Exception as e:
            print_error(f"Failed to get outputs: {e}")
            return False

    async def test_telegram_integration(self):
        """Test 7: Telegram API integration"""
        print_section("Test 7: Telegram Integration")
        
        try:
            import urllib.request
            
            # Test getting agents via Telegram endpoint
            response = urllib.request.urlopen(f"{self.base_url}/telegram/agents")
            agents_data = json.loads(response.read().decode())
            print_success(f"Telegram agents endpoint works")
            print_info(f"  Agents available: {len(agents_data['agents'])}")
            
            # Test sending a Telegram message
            message_data = {
                "chat_id": "test_chat_123",
                "message": "/agents",
                "user_id": "test_user"
            }
            payload = json.dumps(message_data).encode()
            req = urllib.request.Request(
                f"{self.base_url}/telegram/message",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            if result['success']:
                print_success("Telegram message handler works")
                print_info(f"  Response length: {len(result['response'])} chars")
            else:
                print_error(f"Telegram message failed: {result['error']}")
                return False
            
            return True
        except Exception as e:
            print_error(f"Telegram integration test failed: {e}")
            return False

    async def test_tools(self):
        """Test 8: Tool management"""
        print_section("Test 8: Tools")
        
        try:
            import urllib.request
            response = urllib.request.urlopen(f"{self.base_url}/tools")
            tools = json.loads(response.read().decode())
            print_success(f"Retrieved {len(tools)} tools")
            for tool in tools:
                print_info(f"  - {tool['name']}: {tool['description']}")
            return True
        except Exception as e:
            print_error(f"Failed to get tools: {e}")
            return False

    async def run_all_tests(self):
        """Run all tests in sequence"""
        start_time = time.time()
        results = {}
        
        print(f"\n{BLUE}╔════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BLUE}║     Pulse AI End-to-End Integration Test Suite         ║{RESET}")
        print(f"{BLUE}║     {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^54}║{RESET}")
        print(f"{BLUE}╚════════════════════════════════════════════════════════════╝{RESET}")
        
        # Run all tests
        tests = [
            ("Health Check", self.test_health),
            ("Create Agents", self.test_create_agents),
            ("List Agents", self.test_list_agents),
            ("Assign Tasks", self.test_assign_tasks),
            ("Agent Stats", self.test_get_agent_stats),
            ("Outputs", self.test_outputs),
            ("Telegram", self.test_telegram_integration),
            ("Tools", self.test_tools),
        ]
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
            except Exception as e:
                print_error(f"Test crashed: {e}")
                results[test_name] = False
        
        # Print summary
        duration = time.time() - start_time
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        print_section("Test Summary")
        for test_name, result in results.items():
            status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
            print(f"  {status} {test_name}")
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"Results: {GREEN}{passed}/{total} passed{RESET}")
        print(f"Duration: {duration:.2f}s")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        return passed == total

if __name__ == "__main__":
    async def main():
        suite = E2ETestSuite()
        success = await suite.run_all_tests()
        sys.exit(0 if success else 1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
        sys.exit(1)
