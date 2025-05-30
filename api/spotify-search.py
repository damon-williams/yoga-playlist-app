from http.server import BaseHTTPRequestHandler
import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

class handler(BaseHTTPRequestHandler):
    def _get_spotify_client(self):
        """Get Spotify client using Client Credentials flow"""
        try:
            client_id = os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
            
            if not client_id or not client_secret:
                return None
                
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            
            return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        except Exception as e:
            return None

    def do_POST(self):
        # Get POST data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except json.JSONDecodeError:
            self._send_error("Invalid JSON in request body", 400)
            return
        
        playlist_text = data.get('playlist_text', '')
        if not playlist_text:
            self._send_error("Missing playlist_text field", 400)
            return
        
        try:
            # Extract tracks from playlist text and search Spotify
            result = self._search_playlist_tracks(playlist_text)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            return
            
        except Exception as e:
            self._send_error(f"Spotify search failed: {str(e)}", 500)
            return

    def _search_playlist_tracks(self, playlist_text):
        """Extract tracks from playlist text and search Spotify"""
        
        # Extract track listings from playlist text
        tracks = self._extract_tracks_from_text(playlist_text)
        
        if not tracks:
            return {
                "success": False,
                "error": "No tracks found in playlist text"
            }
        
        # Get Spotify client
        sp = self._get_spotify_client()
        if not sp:
            return {
                "success": False,
                "error": "Spotify not configured"
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
                            'preview_url': track['preview_url'],
                            'external_url': track['external_urls']['spotify']
                        }
                    })
                else:
                    failed_tracks.append({
                        'original_query': track_query,
                        'error': 'Track not found on Spotify'
                    })
                    
            except Exception as e:
                failed_tracks.append({
                    'original_query': track_query,
                    'error': str(e)
                })
        
        return {
            "success": True,
            "total_tracks": len(tracks),
            "found_count": len(found_tracks),
            "failed_count": len(failed_tracks),
            "successful_tracks": found_tracks,
            "failed_tracks": failed_tracks,
            "track_ids": [track["spotify_data"]["spotify_id"] for track in found_tracks],
            "ready_for_spotify": len(found_tracks) > 0
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