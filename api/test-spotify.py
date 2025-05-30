from http.server import BaseHTTPRequestHandler
import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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

    def do_GET(self):
        try:
            # Test real Spotify connection
            sp = self._get_spotify_client()
            
            if not sp:
                response = {
                    "success": False,
                    "message": "❌ Spotify credentials not configured",
                    "connected": False
                }
            else:
                # Test with a simple search
                results = sp.search(q="test", type='track', limit=1)
                
                response = {
                    "success": True,
                    "message": "✅ Connected to Spotify API successfully",
                    "connected": True,
                    "test_results": f"Found {len(results['tracks']['items'])} test tracks"
                }
                
        except Exception as e:
            response = {
                "success": False,
                "message": f"❌ Spotify connection failed: {str(e)}",
                "connected": False
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode())
        return