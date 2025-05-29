import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase_client():
    """Create and return Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    return create_client(supabase_url, supabase_key)

def create_yoga_class_types_table():
    """Create the yoga_class_types table using insert/upsert approach"""
    supabase = get_supabase_client()
    
    try:
        # Test if table exists by trying to select from it
        result = supabase.table("yoga_class_types").select("id").limit(1).execute()
        print("✅ Table 'yoga_class_types' already exists!")
        return True
    except Exception:
        # Table doesn't exist, we need to create it
        print("Table doesn't exist. Creating with initial data...")
        
        # Create table by inserting first record (this will auto-create the table)
        initial_data = {
            "name": "Traditional Hatha",
            "description": "Classic yoga with poses held for several breaths, focusing on alignment and breathing",
            "typical_duration": 60,
            "energy_level": "low",
            "music_style_notes": "Soft instrumental, nature sounds, or traditional yoga music"
        }
        
        try:
            result = supabase.table("yoga_class_types").insert(initial_data).execute()
            print("✅ Table 'yoga_class_types' created with initial data!")
            return True
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            return False

def setup_database():
    """Set up all required database tables"""
    print("Setting up database tables...")
    create_yoga_class_types_table()
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()