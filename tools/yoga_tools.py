from langchain.tools import BaseTool
from typing import Dict, Any


class YogaKnowledgeTool(BaseTool):
    name = "yoga_knowledge"
    description = "Access yoga class structure and pose sequence knowledge"
    
    def _run(self, query: str) -> str:
        """Simple yoga knowledge database"""
        yoga_styles = {
            "vinyasa": {
                "description": "Dynamic flow linking breath with movement",
                "phases": ["sun salutations", "standing poses", "peak poses", "seated poses", "relaxation"],
                "typical_duration": "45-90 minutes",
                "music_bpm": "90-120 BPM"
            },
            "yin": {
                "description": "Long-held passive poses, 3-7 minutes each",
                "phases": ["gentle warmup", "long holds", "final relaxation"],
                "typical_duration": "60-90 minutes", 
                "music_bpm": "60-80 BPM"
            },
            "hatha": {
                "description": "Slower-paced with poses held for several breaths",
                "phases": ["warmup", "standing poses", "seated poses", "relaxation"],
                "typical_duration": "60-75 minutes",
                "music_bpm": "70-90 BPM"
            }
        }
        
        # Simple search logic
        query_lower = query.lower()
        for style, info in yoga_styles.items():
            if style in query_lower:
                return f"Style: {style}\n" + "\n".join([f"{k}: {v}" for k, v in info.items()])
        
        return f"Available yoga styles: {list(yoga_styles.keys())}"


# Test the tool
if __name__ == "__main__":
    tool = YogaKnowledgeTool()
    print("Testing Yoga Knowledge Tool:")
    print(tool.run("vinyasa"))