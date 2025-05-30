from http.server import BaseHTTPRequestHandler
import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

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
        required_fields = ['class_name', 'duration']
        for field in required_fields:
            if field not in data:
                self._send_error(f"Missing required field: {field}", 400)
                return

        class_name = data['class_name']
        class_description = data.get('class_description', '')
        music_preferences = data.get('music_preferences', '')
        duration = int(data['duration'])
        
        # Handle empty music preferences
        if not music_preferences.strip():
            music_preferences = "music appropriate for yoga"
            
        try:
            # Handle empty music preferences
            if not music_preferences.strip():
                music_preferences = "music appropriate for yoga"

            # Generate playlist
            playlist = self._generate_real_playlist(class_name, class_description, music_preferences, duration)
            
            # Search for real Spotify tracks
            spotify_results = self._search_spotify_tracks(playlist)
            
            response = {
                "success": True,
                "playlist": playlist,
                "spotify_integration": spotify_results,
                "ready_for_export": len(spotify_results.get("track_ids", [])) > 0,
                "source": "langchain_agent_with_spotify"
            }
            
        except Exception as e:
            # Fallback to mock
            # Handle empty music preferences
            if not music_preferences.strip():
                music_preferences = "music appropriate for yoga"

            playlist = self._generate_mock_playlist(class_name, music_preferences, duration)
            
            response = {
                "success": True,
                "playlist": playlist,
                "spotify_integration": {
                    "search_results": {
                        "found_count": 0,
                        "total_tracks": 0,
                        "error": str(e)
                    },
                    "track_ids": []
                },
                "ready_for_export": False,
                "source": f"fallback_due_to: {str(e)}"
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode())
        return

    def _generate_real_playlist(self, class_name, class_description, music_preferences, duration):
        """Generate playlist using real LangChain agent"""
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        
        llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-3.5-turbo",
            temperature=0.9
        )
        
        prompt = ChatPromptTemplate.from_template("""
        Create a structured playlist for this yoga class that matches the following criteria:
        
        Class Name: {class_name}
        Class Description: {class_description}
        Duration: {duration} minutes
        Music Preferences: {music_preferences}
        
        Ensure the playlist contains enough tracks to cover the entire class duration, with appropriate BPM and energy levels for each section.
                                                  
        Format:
        WARMUP (X minutes)
        Artist - Song Title
        
        FLOW/ACTIVE (X minutes)
        Artist - Song Title
        
        COOLDOWN/SAVASANA (X minutes)
        Artist - Song Title
        """)
        
        chain = prompt | llm
        result = chain.invoke({
            "class_name": class_name,
            "class_description": class_description,
            "duration": duration,
            "music_preferences": music_preferences
        })
        
        return result.content.strip()

    def _search_spotify_tracks(self, playlist_text):
        """Search Spotify for tracks mentioned in the playlist"""
        try:
            # Setup Spotify client
            client_id = os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
            
            if not client_id or not client_secret:
                return {
                    "search_results": {
                        "found_count": 0,
                        "total_tracks": 0,
                        "error": "Spotify credentials not configured"
                    },
                    "track_ids": []
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
                    "search_results": {
                        "found_count": 0,
                        "total_tracks": 0,
                        "error": "No tracks found in playlist text"
                    },
                    "track_ids": []
                }
            
            # Search for each track
            found_tracks = []
            track_ids = []
            
            for track_query in tracks:
                try:
                    # Search Spotify
                    results = sp.search(q=track_query, type='track', limit=1)
                    
                    if results['tracks']['items']:
                        track = results['tracks']['items'][0]
                        found_tracks.append({
                            'original_query': track_query,
                            'spotify_data': {
                                'spotify_id': track['id'],
                                'name': track['name'],
                                'artists': [artist['name'] for artist in track['artists']],
                                'uri': track['uri']
                            }
                        })
                        track_ids.append(track['id'])
                    
                except Exception as search_error:
                    print(f"Error searching for track '{track_query}': {search_error}")
                    continue
            
            return {
                "search_results": {
                    "found_count": len(found_tracks),
                    "total_tracks": len(tracks),
                    "successful_tracks": found_tracks
                },
                "track_ids": track_ids
            }
            
        except Exception as e:
            return {
                "search_results": {
                    "found_count": 0,
                    "total_tracks": 0,
                    "error": f"Spotify search failed: {str(e)}"
                },
                "track_ids": []
            }

    def _extract_tracks_from_text(self, playlist_text):
        """Extract track names from playlist text (same logic as your MusicIntegrationAgent)"""
        tracks = []
        lines = playlist_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for lines that start with • OR - and contain track info
            if (line.startswith('•') or line.startswith('-')) and ' - ' in line:
                # Remove the bullet point or dash and clean up
                if line.startswith('•'):
                    track_info = line[1:].strip()
                elif line.startswith('-'):
                    track_info = line[1:].strip()
                tracks.append(track_info)
        
        return tracks

    def _generate_mock_playlist(self, class_name, music_preferences, duration):
        """Fallback mock playlist"""
        warmup_duration = int(duration * 0.15)
        flow_duration = int(duration * 0.45)
        peak_duration = int(duration * 0.25)
        cooldown_duration = int(duration * 0.15)
        
        return f"""**WARMUP ({warmup_duration} minutes)**
BPM: 70-85 | Energy: Building, welcoming
- Sample Artist - Sample Song 1

**FLOW/ACTIVE ({flow_duration} minutes)**
BPM: 90-110 | Energy: Sustained, rhythmic
- Sample Artist - Sample Song 2

**PEAK ({peak_duration} minutes)**
BPM: 100-120 | Energy: High intensity
- Sample Artist - Sample Song 3

**COOLDOWN/SAVASANA ({cooldown_duration} minutes)**
BPM: 60-75 | Energy: Peaceful
- Sample Artist - Sample Song 4"""

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_error(self, message, status_code):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"success": False, "error": message}
        self.wfile.write(json.dumps(response).encode())