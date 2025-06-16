from http.server import BaseHTTPRequestHandler
import json
import os
from supabase import create_client

class handler(BaseHTTPRequestHandler):
    def _get_supabase_client(self):
        """Get Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        return create_client(supabase_url, supabase_key)

    def do_GET(self):
        try:
            # Get user_id from query parameters
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            user_id = query_params.get('user_id', [None])[0]
            
            print(f"[DEBUG] Fetching classes for user_id: {user_id}")
            
            # Get real data from Supabase
            supabase = self._get_supabase_client()
            
            # Build query: public classes OR user's private classes
            if user_id:
                # Get public classes AND user's private classes
                result = supabase.table("yoga_class_types").select("name, description, user_id, is_public").or_(f"is_public.eq.true,user_id.eq.{user_id}").order("is_public", desc=True).order("created_at", desc=False).execute()
            else:
                # Only get public classes if no user_id provided
                result = supabase.table("yoga_class_types").select("name, description, user_id, is_public").eq("is_public", True).order("created_at", desc=False).execute()
            
            classes = []
            if result.data:
                for row in result.data:
                    classes.append({
                        "name": row["name"],
                        "description": row["description"],
                        "is_custom": not row.get("is_public", False),
                        "user_id": row.get("user_id")
                    })
            
            print(f"[DEBUG] Found {len(classes)} classes")
            
            response = {
                "success": True,
                "classes": classes,
                "total": len(classes)
            }
            
        except Exception as e:
            # Fallback to hardcoded classes if Supabase fails
            classes = [
                {
                    "name": "Traditional Hatha",
                    "description": "Classic yoga with poses held for several breaths, focusing on alignment and breathing"
                },
                {
                    "name": "Vinyasa Flow", 
                    "description": "Dynamic flow linking breath with movement"
                },
                {
                    "name": "Yoga Sculpt",
                    "description": "Fitness-integrated yoga with strength training elements using weights"
                }
            ]
            
            response = {
                "success": True,
                "classes": classes,
                "total": len(classes),
                "note": f"Using fallback data due to: {str(e)}"
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode())
        return

    def do_POST(self):
        # Get POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except json.JSONDecodeError:
            self._send_error("Invalid JSON in request body", 400)
            return
        
        # Validate required fields
        if not data.get('name') or not data.get('description'):
            self._send_error("Missing required fields: name and description", 400)
            return
        
        # Get user_id - for custom classes, this should be provided
        user_id = data.get('user_id')
        
        print(f"[DEBUG] Creating class '{data['name']}' for user_id: {user_id}")
        
        try:
            # Add to real Supabase database
            supabase = self._get_supabase_client()
            
            insert_data = {
                "name": data['name'],
                "description": data['description'],
                "typical_duration": data.get('duration'),
                "energy_level": data.get('energy_level'),
                "music_style_notes": data.get('music_style_notes'),
                "user_id": user_id,
                "is_public": data.get('is_public', False)  # Default to private
            }
            
            result = supabase.table("yoga_class_types").insert(insert_data).execute()
            
            response = {
                "success": True,
                "message": f"✅ Added class type: {data['name']}",
                "class": {
                    "name": data['name'],
                    "description": data['description']
                }
            }
            
        except Exception as e:
            self._send_error(f"Database error: {str(e)}", 500)
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode())
        return

    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_error(self, message, status_code):
        """Helper to send error responses"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "success": False,
            "error": message
        }
        
        self.wfile.write(json.dumps(response).encode())