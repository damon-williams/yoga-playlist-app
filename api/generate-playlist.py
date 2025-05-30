from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
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
        required_fields = ['class_name', 'music_preferences', 'duration']
        for field in required_fields:
            if field not in data:
                self._send_error(f"Missing required field: {field}", 400)
                return

        class_name = data['class_name']
        music_preferences = data['music_preferences']
        duration = int(data['duration'])
        
        # Generate mock playlist based on preferences
        mock_playlist = self._generate_mock_playlist(class_name, music_preferences, duration)
        
        response = {
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
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _generate_mock_playlist(self, class_name, music_preferences, duration):
        """Generate a mock playlist based on input parameters"""
        
        # Calculate phase durations
        warmup_duration = int(duration * 0.15)
        flow_duration = int(duration * 0.45)
        peak_duration = int(duration * 0.25)
        cooldown_duration = int(duration * 0.15)
        
        # Sample tracks based on music preferences
        if "hip-hop" in music_preferences.lower() or "hip hop" in music_preferences.lower():
            tracks = {
                "warmup": ["Lauryn Hill - Ex-Factor", "Erykah Badu - On & On"],
                "flow": ["Tupac - California Love", "Biggie - Juicy", "Nas - The World Is Yours"],
                "peak": ["Jay-Z - 99 Problems", "Eminem - Lose Yourself"],
                "cooldown": ["Common - The Light", "Lauryn Hill - To Zion"]
            }
        elif "electronic" in music_preferences.lower():
            tracks = {
                "warmup": ["Lane 8 - Brightest Lights", "Marsh - Belle"],
                "flow": ["Rufus Du Sol - Innerbloom", "Disclosure - Magnets", "Flume - Never Be Like You"],
                "peak": ["ZHU - Faded", "ODESZA - Bloom"],
                "cooldown": ["Bonobo - Cirrus", "Tycho - A Walk"]
            }
        elif "country" in music_preferences.lower():
            tracks = {
                "warmup": ["Brett Eldredge - Love Someone", "Kacey Musgraves - Slow Burn"],
                "flow": ["Keith Urban - Never Comin' Down", "Miranda Lambert - Little Red Wagon", "Thomas Rhett - Vacation"],
                "peak": ["Carrie Underwood - Before He Cheats", "Luke Bryan - Country Girl"],
                "cooldown": ["Dan + Shay - Speechless", "Chris Stapleton - Tennessee Whiskey"]
            }
        else:
            # Default indie/alternative playlist
            tracks = {
                "warmup": ["Bon Iver - Holocene", "Iron & Wine - Walking Far from Home"],
                "flow": ["Alt-J - Left Hand Free", "Tame Impala - Feels Like We Only Go Backwards", "Arctic Monkeys - Do I Wanna Know"],
                "peak": ["Foster the People - Pumped Up Kicks", "MGMT - Electric Feel"],
                "cooldown": ["Sufjan Stevens - Mystery of Love", "The National - I Need My Girl"]
            }
        
        # Build playlist string
        playlist = f"""**WARMUP ({warmup_duration} minutes)**
BPM: 70-85 | Energy: Building, welcoming"""
        
        for track in tracks["warmup"]:
            playlist += f"\n- {track}"
            
        playlist += f"""

**FLOW/ACTIVE ({flow_duration} minutes)**
BPM: 90-110 | Energy: Sustained, rhythmic"""
        
        for track in tracks["flow"]:
            playlist += f"\n- {track}"
            
        playlist += f"""

**PEAK ({peak_duration} minutes)**
BPM: 100-120 | Energy: High intensity, motivating"""
        
        for track in tracks["peak"]:
            playlist += f"\n- {track}"
            
        playlist += f"""

**COOLDOWN/SAVASANA ({cooldown_duration} minutes)**
BPM: 60-75 | Energy: Peaceful, meditative"""
        
        for track in tracks["cooldown"]:
            playlist += f"\n- {track}"
            
        return playlist

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