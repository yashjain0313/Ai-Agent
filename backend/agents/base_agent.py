"""
Base Agent Class for Multi-Agent System
All agents inherit from this base class for consistent structure
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import os
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgent(ABC):
    """Abstract base class for all agents in the system"""
    
    def __init__(self, agent_name: str, temperature: float = 0):
        """
        Initialize base agent with Gemini 2.5 Flash-Lite
        
        Args:
            agent_name: Name/identifier for this agent
            temperature: LLM temperature (0 = deterministic, 1 = creative)
        """
        self.agent_name = agent_name
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=temperature,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Main execution method - must be implemented by each agent
        
        Returns:
            Dict containing agent output
        """
        pass
    
    def log(self, message: str):
        """Log agent activity"""
        print(f"[{self.agent_name}] {message}")
