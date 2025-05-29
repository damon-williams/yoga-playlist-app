from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool
from config.settings import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE


class BaseYogaAgent(ABC):
    """Base class for all yoga playlist agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model_name=MODEL_NAME,
            temperature=TEMPERATURE
        )
        self.memory = ConversationBufferMemory(return_messages=True)
        self.tools = self._setup_tools()
        
    @abstractmethod
    def _setup_tools(self) -> List[BaseTool]:
        """Each agent defines its own tools"""
        pass
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Each agent defines its own system prompt"""
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Return basic info about this agent"""
        return {
            "name": self.name,
            "tools": [tool.name for tool in self.tools],
            "model": MODEL_NAME
        }