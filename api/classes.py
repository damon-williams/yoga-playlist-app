from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Return hardcoded classes for now
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
            "total": len(classes)
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
            
        # Mock success response
        response = {
            "success": True,
            "message": f"✅ Added class type: {data['name']}",
            "class": {
                "name": data['name'],
                "description": data['description']
            }
        }
        
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