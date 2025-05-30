from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add paths for importing agents
sys.path.append('/tmp')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        
        try:
            # Try to use real LangChain agent
            playlist = self._generate_real_playlist(class_name, music_preferences, duration)
            
            # Search for real tracks on Spotify
            spotify_result = self._search_spotify_tracks(playlist)
            
            response = {
                "success": True,
                "playlist": playlist,
                "spotify_integration": spotify_result,
                "ready_for_export": spotify_result.get("ready_for_spotify", False),
                "source": "langchain_agent"
            }
            
        except Exception as e:
            # Fallback to mock if LangChain fails
            playlist = self._generate_mock_playlist(class_name, music_preferences, duration)
            
            response = {
                "success": True,
                "playlist": playlist,
                "spotify_integration": {
                    "search_results": {
                        "found_count": 8,
                        "total_tracks": 8
                    },
                    "track_ids": ["mock_id_1", "mock_id_2", "mock_id_3", "mock_id_4", "mock_id_5", "mock_id_6", "mock_id_7", "mock_id_8"]
                },
                "ready_for_export": True,
                "source": f"fallback_due_to: {str(e)}"
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode())
        return

    def _generate_real_playlist(self, class_name, music_preferences, duration):
        """Generate playlist using real LangChain agent"""
        
        # Import LangChain components
        from langchain_openai import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate
        
        # Initialize LLM
        llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # Create prompt
        prompt = ChatPromptTemplate.from_template("""
        You are a music curation expert for yoga classes. Create a structured playlist for this yoga class.
        
        Class: {class_name}
        Duration: {duration} minutes
        Music Preferences: {music_preferences}
        
        IMPORTANT: Your response should ONLY contain the structured playlist format below. 
        Do not include any explanatory text, introductions, or commentary.
        
        Always use this exact format:
        
        **WARMUP (X minutes)**
        BPM: XX-XX | Energy: Description
        - Artist - Song Title
        - Artist - Song Title
        
        **FLOW/ACTIVE (X minutes)**
        BPM: XX-XX | Energy: Description  
        - Artist - Song Title
        - Artist - Song Title
        
        **PEAK (X minutes)**
        BPM: XX-XX | Energy: Description
        - Artist - Song Title
        - Artist - Song Title
        
        **COOLDOWN/SAVASANA (X minutes)**
        BPM: XX-XX | Energy: Description
        - Artist - Song Title
        - Artist - Song Title
        
        Key principles:
        - Warmup: 60-80 BPM, gentle, welcoming
        - Flow: 80-110 BPM, rhythmic, supportive
        - Peak: 90-120 BPM, energizing, focused
        - Cooldown: 50-70 BPM, peaceful, integrative
        
        Match the teacher's music preferences and class style when selecting tracks.
        """)
        
        # Generate playlist
        chain = prompt | llm
        result = chain.invoke({
            "class_name": class_name,
            "duration": duration,
            "music_preferences": music_preferences
        })
        
        return result.content.strip()

    def _generate_mock_playlist(self, class_name, music_preferences, duration):
        """Fallback mock playlist generation"""
        
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
            
            def _search_spotify_tracks(self, playlist_text):
        """Search for tracks on Spotify"""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyClientCredentials
            
            # Get Spotify client
            client_id = os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
            
            if not client_id or not client_secret:
                return {
                    "found_count": 0,
                    "total_tracks": 0,
                    "ready_for_spotify": False,
                    "error": "Spotify credentials not configured"
                }
            
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            
            sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            
            # Extract tracks from playlist text
            tracks = self._extract_tracks_from_text(playlist_text)
            
            if not tracks:
                return {
                    "found_count": 0,
                    "total_tracks": 0,
                    "ready_for_spotify": False,
                    "error": "No tracks found in playlist"
                }
            
            # Search for each track
            found_tracks = []
            failed_tracks = []
            
            for track_query in tracks:
                try:
                    search_results = sp.search(q=track_query, type='track', limit=1)
                    tracks_found = search_results['tracks']['items']
                    
                    if tracks_found:
                        track = tracks_found[0]
                        found_tracks.append({
                            'original_query': track_query,
                            'spotify_data': {
                                'spotify_id': track['id'],
                                'name': track['name'],
                                'artists': [artist['name'] for artist in track['artists']],
                                'duration_ms': track['duration_ms'],
                                'preview_url': track['preview_url']
                            }
                        })
                    else:
                        failed_tracks.append({
                            'original_query': track_query,
                            'error': 'Track not found'
                        })
                        
                except Exception as e:
                    failed_tracks.append({
                        'original_query': track_query,
                        'error': str(e)
                    })
            
            return {
                "search_results": {
                    "found_count": len(found_tracks),
                    "total_tracks": len(tracks),
                    "successful_tracks": found_tracks,
                    "failed_tracks": failed_tracks
                },
                "track_ids": [track["spotify_data"]["spotify_id"] for track in found_tracks],
                "ready_for_spotify": len(found_tracks) > 0
            }
            
        except Exception as e:
            return {
                "found_count": 0,
                "total_tracks": 0,
                "ready_for_spotify": False,
                "error": f"Spotify search failed: {str(e)}"
            }

    def _extract_tracks_from_text(self, playlist_text):
        """Extract track listings from playlist text"""
        tracks = []
        lines = playlist_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for lines with track format: "- Artist - Song"
            if line.startswith('-') and ' - ' in line[1:]:
                track = line[1:].strip()  # Remove the dash
                tracks.append(track)
        
        return tracks

    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
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