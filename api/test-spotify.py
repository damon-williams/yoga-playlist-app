from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # TODO: Test actual Spotify connection
        # For now, return mock connection status
        response = {
            "success": True,
            "message": "✅ Connected to Spotify as: Demo User (demo_user_id)",
            "connected": True
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode())
        return