import os
import sys
from typing import List
from langchain.tools import BaseTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.yoga_tools import YogaKnowledgeTool
from config.settings import OPENAI_API_KEY

load_dotenv()

class MusicCurationAgent:
    """Specializes in finding and recommending music for yoga classes"""
    
    def __init__(self):
        self.name = "MusicCuration"
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        self.tools = [YogaKnowledgeTool()]
        self.agent_executor = self._create_agent_executor()
    
    def _get_system_prompt(self) -> str:
        return """You are the Music Curation Agent for a yoga playlist system.
        
        Your role is to create structured playlists for yoga classes based on class type and music preferences.
        
        IMPORTANT: Your response should ONLY contain the structured playlist format below. 
        Do not include any explanatory text, introductions, or commentary.
        
        Always use this exact format:
        
        **WARMUP (X minutes)**
        BPM: XX-XX | Energy: Description
        - Artist - Song Title
        - Artist - Song Title
        
        **FLOW/ACTIVE (X minutes)**
        BPM: XX-XX | Energy: Description  
        - Artist - Song Title
        - Artist - Song Title
        
        **PEAK (X minutes)**
        BPM: XX-XX | Energy: Description
        - Artist - Song Title
        - Artist - Song Title
        
        **COOLDOWN/SAVASANA (X minutes)**
        BPM: XX-XX | Energy: Description
        - Artist - Song Title
        - Artist - Song Title
        
        Key principles:
        - Warmup: 60-80 BPM, gentle, welcoming
        - Flow: 80-110 BPM, rhythmic, supportive
        - Peak: 90-120 BPM, energizing, focused
        - Cooldown: 50-70 BPM, peaceful, integrative
        
        Match the teacher's music preferences and class style when selecting tracks."""
    
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
    
    def recommend_music(self, class_info: str, music_preferences: str, duration_minutes: int = 60) -> str:
        """Get a structured playlist for a specific class"""
        request = f"""
        Create a complete start-to-finish playlist for this yoga class:
        
        Class Info: {class_info}
        Duration: {duration_minutes} minutes
        Teacher's Music Preferences: {music_preferences}
        
        Provide a structured playlist with these sections:
        1. WARMUP (first 15% of class)
        2. FLOW/ACTIVE (next 45% of class) 
        3. PEAK (next 25% of class)
        4. COOLDOWN/SAVASANA (final 15% of class)
        
        For each section, provide:
        - Duration in minutes
        - 3-5 specific track suggestions with Artist - Song Title
        - Target BPM range
        - Brief energy description
        
        Format like this:
        **WARMUP (X minutes)**
        BPM: XX-XX | Energy: Description
        • Artist - Song Title
        • Artist - Song Title
        
        Make the track suggestions as specific as possible based on the music preferences.
        """
        
        try:
            result = self.agent_executor.invoke({
                "input": request,
                "chat_history": []
            })
            return result["output"]
        except Exception as e:
            return f"Error creating playlist: {str(e)}"

# Test the agent
if __name__ == "__main__":
    agent = MusicCurationAgent()
    
    print("=== Testing Music Curation Agent ===")
    
    # Test with Jenny's Yoga Sculpt class
    print("\n1. Getting recommendations for Jenny's Yoga Sculpt:")
    response = agent.recommend_music(
        class_info="High-energy fitness yoga with weights, 60 minutes, strength building focus",
        music_preferences="90s-00s hip-hop - artists like Tupac, Biggie, Lauryn Hill",
        duration_minutes=60
    )
    print(f"Playlist:\n{response}")
    
    print("\n" + "="*50)
    
    # Test with Eve's Foundations class
    print("\n2. Getting recommendations for Eve's Foundations:")
    response = agent.recommend_music(
        class_info="Basic yoga poses with detailed instruction, 75 minutes, beginner-friendly",
        music_preferences="Downtempo trip-hop like Massive Attack, Portishead"
    )
    print(f"Music recommendations:\n{response}")