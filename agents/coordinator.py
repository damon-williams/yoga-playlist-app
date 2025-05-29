import os
import sys
from typing import List, Dict
from langchain.tools import BaseTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.class_management import ClassManagementAgent
from agents.music_curation import MusicCurationAgent
from config.settings import OPENAI_API_KEY

load_dotenv()

class CoordinatorAgent:
    """Orchestrates multiple agents to generate complete yoga playlists"""
    
    def __init__(self):
        self.name = "Coordinator"
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # Initialize sub-agents
        self.class_manager = ClassManagementAgent()
        self.music_curator = MusicCurationAgent()
        
        print(f"✅ Coordinator initialized with {len(self._get_sub_agents())} sub-agents")
    
    def _get_sub_agents(self) -> Dict[str, object]:
        """Return dictionary of available sub-agents"""
        return {
            "class_management": self.class_manager,
            "music_curation": self.music_curator
        }
    
    def generate_playlist(self, class_name: str, music_preferences: str, duration: int = 60) -> Dict:
        """Main coordination method - generates complete playlist"""
        
        print(f"🎯 Coordinator: Starting playlist generation")
        print(f"   Class: {class_name}")
        print(f"   Music Style: {music_preferences}")
        print(f"   Duration: {duration} minutes")
        
        try:
            # Step 1: Get class information
            print("\n📚 Step 1: Getting class information...")
            class_info = self.class_manager.process_request(
                f"Tell me about the '{class_name}' yoga class type. What are its characteristics?"
            )
            
            # Step 2: Generate music playlist
            print("\n🎵 Step 2: Creating music playlist...")
            playlist = self.music_curator.recommend_music(
                class_info=class_info,
                music_preferences=music_preferences,
                duration_minutes=duration
            )
            
            # Step 3: Package results
            result = {
                "success": True,
                "class_name": class_name,
                "class_info": class_info,
                "duration_minutes": duration,
                "music_preferences": music_preferences,
                "playlist": playlist,
                "generated_by": "Coordinator Agent"
            }
            
            print("\n✅ Coordinator: Playlist generation complete!")
            return result
            
        except Exception as e:
            print(f"\n❌ Coordinator: Error during generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "class_name": class_name
            }
    
    def list_available_classes(self) -> str:
        """Get list of available yoga classes"""
        return self.class_manager.process_request("What yoga class types are available?")


# Test the coordinator
if __name__ == "__main__":
    coordinator = CoordinatorAgent()
    
    print("=== Testing Coordinator Agent ===")
    
    # Test 1: List available classes
    print("\n1. Getting available classes:")
    classes = coordinator.list_available_classes()
    print(classes)
    
    print("\n" + "="*60)
    
    # Test 2: Generate playlist for Jenny's style
    print("\n2. Generating playlist for Yoga Sculpt:")
    result = coordinator.generate_playlist(
        class_name="Yoga Sculpt",
        music_preferences="90s-00s hip-hop",
        duration=60
    )
    
    if result["success"]:
        print(f"\n🎉 SUCCESS! Generated playlist:")
        print(f"Class: {result['class_name']}")
        print(f"Duration: {result['duration_minutes']} minutes")
        print(f"\nPlaylist:\n{result['playlist']}")
    else:
        print(f"\n❌ FAILED: {result['error']}")