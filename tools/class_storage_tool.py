import os
from supabase import create_client
from langchain.tools import BaseTool
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class ClassStorageTool(BaseTool):
    name = "class_storage"
    description = "Store and retrieve custom yoga class types from database"
    
    def _get_supabase_client(self):
        """Get Supabase client when needed"""
        return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    def _run(self, query: str) -> str:
        """Run the tool with a query string"""
        # Parse the query - for now, let's handle it simply
        if query == "list_all":
            return self._list_all_class_types()
        else:
            return f"Query: {query} - Tool is working!"
    
    def _add_class_type(self, name: str, description: str, 
                       typical_duration: Optional[int] = None,
                       energy_level: Optional[str] = None,
                       music_style_notes: Optional[str] = None) -> str:
        """Add a new class type to the database"""
        
        supabase = self._get_supabase_client()
        
        data = {
            "name": name,
            "description": description,
            "typical_duration": typical_duration,
            "energy_level": energy_level,
            "music_style_notes": music_style_notes
        }
        
        result = supabase.table("yoga_class_types").insert(data).execute()
        return f"✅ Added class type: {name}"
    
    def _search_class_types(self, query: str) -> str:
        """Search for class types by name or description"""
        
        supabase = self._get_supabase_client()
        result = supabase.table("yoga_class_types").select("*").ilike("name", f"%{query}%").execute()
        
        if result.data:
            classes = []
            for class_type in result.data:
                classes.append(f"• {class_type['name']}: {class_type['description']}")
            return "\n".join(classes)
        else:
            return f"No class types found matching '{query}'"
    
    def _list_all_class_types(self) -> str:
        """List all available class types"""
        
        supabase = self._get_supabase_client()
        result = supabase.table("yoga_class_types").select("*").order("created_at", desc=True).execute()
        
        if result.data:
            classes = []
            for class_type in result.data:
                classes.append(f"• {class_type['name']}: {class_type['description']}")
            return "\n".join(classes)
        else:
            return "No class types available yet."


# Test the tool
if __name__ == "__main__":
    tool = ClassStorageTool()
    
    print("=== Testing Class Storage Tool ===")
    
    # Test listing existing classes
    print("\n1. Listing all classes:")
    result = tool.run("list_all")
    print(result)
    
    # Test basic functionality
    print("\n2. Testing basic query:")
    result = tool.run("test query")
    print(result)