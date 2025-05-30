from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path to determine which endpoint
        path = self.path
        
        if path == '/api/health':
            self._send_json_response({
                "status": "healthy",
                "message": "API is working",
                "timestamp": "2024-01-01T00:00:00Z"
            })
        elif path == '/api/classes':
            self._handle_get_classes()
        elif path == '/api/test-spotify':
            self._handle_test_spotify()
        else:
            self._send_json_response({
                "message": "Yoga Playlist API is running!",
                "status": "healthy",
                "available_endpoints": ["/api/health", "/api/classes", "/api/test-spotify"]
            })

    def do_POST(self):
        # Parse the path to determine which endpoint
        path = self.path
        
        # Get POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except json.JSONDecodeError:
            self._send_error_response("Invalid JSON in request body", 400)
            return
        
        if path == '/api/generate-playlist':
            self._handle_generate_playlist(data)
        elif path == '/api/classes':
            self._handle_add_class(data)
        elif path == '/api/create-spotify-playlist':
            self._handle_create_spotify_playlist(data)
        else:
            self._send_error_response("Endpoint not found", 404)

    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_json_response(self, data, status_code=200):
        """Helper to send JSON responses"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(data)
        self.wfile.write(response_json.encode())

    def _send_error_response(self, message, status_code=500):
        """Helper to send error responses"""
        self._send_json_response({
            "success": False,
            "error": message
        }, status_code)

    def _handle_get_classes(self):
        """Handle GET /api/classes - return hardcoded classes for now"""
        # TODO: Replace with actual database integration
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
        
        self._send_json_response({
            "success": True,
            "classes": classes,
            "total": len(classes)
        })

    def _handle_add_class(self, data):
        """Handle POST /api/classes - add new class"""
        # Validate required fields
        if not data.get('name') or not data.get('description'):
            self._send_error_response("Missing required fields: name and description", 400)
            return
            
        # TODO: Add to actual database
        # For now, just return success
        self._send_json_response({
            "success": True,
            "message": f"✅ Added class type: {data['name']}",
            "class": {
                "name": data['name'],
                "description": data['description']
            }
        })

    def _handle_generate_playlist(self, data):
        """Handle POST /api/generate-playlist"""
        # Validate required fields
        required_fields = ['class_name', 'music_preferences', 'duration']
        for field in required_fields:
            if field not in data:
                self._send_error_response(f"Missing required field: {field}", 400)
                return

        # TODO: Integrate with actual agents
        # For now, return a mock playlist
        mock_playlist = f"""**WARMUP (9 minutes)**
BPM: 70-85 | Energy: Building, welcoming  
- Sample Artist - Sample Song 1
- Sample Artist - Sample Song 2

**FLOW (27 minutes)**
BPM: 90-110 | Energy: Sustained, rhythmic
- Sample Artist - Sample Song 3
- Sample Artist - Sample Song 4

**PEAK (15 minutes)**  
BPM: 100-120 | Energy: High intensity
- Sample Artist - Sample Song 5
- Sample Artist - Sample Song 6

**COOLDOWN (9 minutes)**
BPM: 60-75 | Energy: Peaceful
- Sample Artist - Sample Song 7
- Sample Artist - Sample Song 8"""

        self._send_json_response({
            "success": True,
            "playlist": mock_playlist,
            "spotify_integration": {
                "search_results": {
                    "found_count": 8,
                    "total_tracks": 8
                },
                "track_ids": ["mock_id_1", "mock_id_2", "mock_id_3", "mock_id_4", "mock_id_5", "mock_id_6", "mock_id_7", "mock_id_8"]
            },
            "ready_for_export": True
        })

    def _handle_create_spotify_playlist(self, data):
        """Handle POST /api/create-spotify-playlist"""
        # Validate required fields
        if not data.get('playlist_name') or not data.get('track_ids'):
            self._send_error_response("Missing required fields: playlist_name and track_ids", 400)
            return

        # TODO: Integrate with actual Spotify API
        # For now, return mock success
        self._send_json_response({
            "success": True,
            "message": f"✅ Created playlist '{data['playlist_name']}' with {len(data['track_ids'])} tracks: https://open.spotify.com/playlist/mock_id",
            "playlist_created": True
        })

    def _handle_test_spotify(self):
        """Handle GET /api/test-spotify"""
        # TODO: Test actual Spotify connection
        # For now, return mock connection
        self._send_json_response({
            "success": True,
            "message": "✅ Connected to Spotify as: Mock User (mock_user)",
            "connected": True
        })