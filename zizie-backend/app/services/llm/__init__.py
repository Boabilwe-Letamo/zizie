"""
LLM Service - Unified interface for local and cloud LLMs
"""
import httpx
from typing import Optional, List, Dict, Any

from app.core.config import settings


class LLMService:
    """Unified LLM service supporting multiple backends."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate chat completion."""
        
        # Try HuggingFace Inference API first
        if settings.HF_INFERENCE and settings.HUGGINGFACE_TOKEN:
            try:
                return await self._hf_inference(messages, system_prompt)
            except Exception as e:
                print(f"HuggingFace failed: {e}")
        
        # Try Ollama
        if settings.OLLAMA_BASE_URL:
            try:
                return await self._ollama_chat(messages, system_prompt)
            except Exception as e:
                print(f"Ollama failed: {e}")
        
        # Fallback to mock response
        return self._mock_response(messages)
    
    async def _hf_inference(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Use HuggingFace Inference API."""
        import urllib.parse
        
        # Build prompt from messages
        prompt = ""
        if system_prompt:
            prompt = f"System: {system_prompt}\n"
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"{role}: {content}\n"
        
        prompt += "assistant: "
        
        # API endpoint
        url = f"https://api-inference.huggingface.co/models/{settings.HF_MODEL}"
        
        headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 256,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        response = await self.client.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")[:500]
        
        raise Exception(f"HF Inference failed: {response.status_code}")
    
    async def _ollama_chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Use Ollama for local LLM."""
        
        # Build messages format for Ollama
        ollama_messages = []
        if system_prompt:
            ollama_messages.append({"role": "system", "content": system_prompt})
        ollama_messages.extend(messages)
        
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": ollama_messages,
            "stream": False
        }
        
        response = await self.client.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("message", {}).get("content", "")
        
        raise Exception(f"Ollama failed: {response.status_code}")
    
    def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Mock response for testing."""
        last_msg = messages[-1].get("content", "") if messages else ""
        
        responses = {
            "email": "I've drafted the email. Would you like me to send it?",
            "meeting": "I've scheduled the meeting. Should I send calendar invites?",
            "reminder": "Reminder created. I'll notify you at the specified time.",
            "note": "Note saved. Anything else you'd like me to record?",
            "call": "I'll remind you to make that call."
        }
        
        for key, response in responses.items():
            if key in last_msg.lower():
                return response
        
        return "I've processed your request. Would you like me to do anything else?"
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()


# Service instance
llm_service = LLMService()