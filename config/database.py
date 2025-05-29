import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables directly
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    """Create and return Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Test connection
if __name__ == "__main__":
    try:
        supabase = get_supabase_client()
        print("✅ Supabase connection successful!")
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")