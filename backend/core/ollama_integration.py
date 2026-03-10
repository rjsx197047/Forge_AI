"""
Ollama Integration Module
Handles all interactions with Ollama AI models running locally
"""
import requests
import asyncio
from typing import Optional, Dict, Any
import json

class OllamaIntegration:
    """
    Integration with Ollama AI for running LLMs locally
    Supports models like: llama2, mistral, neural-chat, starling-lm, etc.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api"
        self.available_models = []
        
    async def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            print(f"[Ollama] Connection check failed: {e}")
            return False
    
    async def get_available_models(self) -> list:
        """Fetch list of available models from Ollama"""
        try:
            response = requests.get(f"{self.api_endpoint}/tags")
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                self.available_models = models
                return models
            return []
        except Exception as e:
            print(f"[Ollama] Error fetching models: {e}")
            return []
    
    async def generate_response(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 512
    ) -> str:
        """
        Generate response from Ollama model
        
        Args:
            model: Name of the Ollama model (e.g., "llama2", "mistral")
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            temperature: Randomness (0.0-1.0)
            top_p: Nucleus sampling parameter
            max_tokens: Maximum response length
            
        Returns:
            Generated text response
        """
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens
            }
            
            response = requests.post(
                f"{self.api_endpoint}/generate",
                json=payload,
                timeout=300  # 5 minute timeout for model inference
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', 'No response generated')
            else:
                return f"Error: Ollama returned status {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "Error: Request timeout. Model may be processing a large request."
        except Exception as e:
            print(f"[Ollama] Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
    async def execute_task(
        self,
        model: str,
        task: str,
        agent_role: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using Ollama model with agent context
        
        Args:
            model: Ollama model name
            task: Task description
            agent_role: Role of the agent (helps with context)
            context: Additional context or memory
            
        Returns:
            Dict with status, output, and metadata
        """
        try:
            system_prompt = f"You are a {agent_role} assistant." if agent_role else "You are a helpful assistant."
            if context:
                system_prompt += f"\nContext: {context}"
            
            response = await self.generate_response(
                model=model,
                prompt=task,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1024
            )
            
            return {
                "status": "success",
                "output": response,
                "model": model,
                "task": task,
                "error": None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "output": None,
                "model": model,
                "task": task,
                "error": str(e)
            }
    
    async def pull_model(self, model_name: str) -> bool:
        """
        Download/pull a model from Ollama registry
        
        Args:
            model_name: Name of model to pull (e.g., "llama2", "mistral")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {"name": model_name}
            response = requests.post(
                f"{self.api_endpoint}/pull",
                json=payload,
                timeout=3600  # 1 hour timeout for large downloads
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[Ollama] Error pulling model: {e}")
            return False

# Singleton instance
ollama_integration = OllamaIntegration()
