import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def test_database():
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    try:
        result = supabase.table("yoga_class_types").select("*").execute()
        print("✅ Database connection successful!")
        print(f"Found {len(result.data)} class types:")
        for class_type in result.data:
            print(f"  • {class_type['name']}: {class_type['description']}")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database()