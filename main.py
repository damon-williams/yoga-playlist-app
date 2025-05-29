from config.settings import OPENAI_API_KEY
from agents.coordinator import CoordinatorAgent

if __name__ == "__main__":
    if OPENAI_API_KEY:
        print("✅ Environment setup successful!")
        
        # Test the Coordinator Agent
        coordinator = CoordinatorAgent()
        print(f"🎯 Created {coordinator.name} agent")
        print(f"📊 Agent info: {coordinator.get_agent_info()}")
        
        print("Ready to build more agents!")
    else:
        print("❌ OpenAI API key not found. Check your .env file.")