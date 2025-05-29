import os
import sys
from typing import List
from langchain.tools import BaseTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.class_storage_tool import ClassStorageTool
from config.settings import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE

load_dotenv()

class ClassManagementAgent:
    """Manages yoga class types - can add new classes and search existing ones"""
    
    def __init__(self):
            self.name = "ClassManagement"
            self.llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model_name=MODEL_NAME
            )
            self.tools = [ClassStorageTool()]
            self.agent_executor = self._create_agent_executor()

    def _setup_tools(self) -> List[BaseTool]:
        return [ClassStorageTool()]
    
    def _get_system_prompt(self) -> str:
        return """You are the Class Management Agent for a yoga playlist system.
        
        Your role is to:
        1. Help teachers add new custom class types to the database
        2. Search existing class types 
        3. Provide information about available class styles
        
        You have access to a class_storage tool that can:
        - list_all: Show all available class types
        - More functions coming soon for adding and searching
        
        Always be helpful and knowledgeable about different yoga styles."""
    
    def _create_agent_executor(self):
        """Create the LangChain agent executor"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def process_request(self, user_input: str) -> str:
        """Process a user request using the agent"""
        try:
            result = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": []
            })
            return result["output"]
        except Exception as e:
            return f"Error processing request: {str(e)}"


# Test the agent
if __name__ == "__main__":
    agent = ClassManagementAgent()
    
    print("=== Testing Class Management Agent ===")
    
    # Test 1: List all classes
    print("\n1. Asking agent to list all class types:")
    response = agent.process_request("What yoga class types are available?")
    print(f"Agent response: {response}")