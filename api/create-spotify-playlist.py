from http.server import BaseHTTPRequestHandler
import json
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import urllib.parse

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
        
        # Check if this is an auth callback or playlist creation
        action = data.get('action', 'create_playlist')
        
        print(f"[DEBUG] Received action: {action}")
        
        if action == 'get_auth_url':
            self._handle_get_auth_url()
        elif action == 'create_playlist':
            # Validate required fields for playlist creation
            required_fields = ['playlist_name', 'track_ids']
            for field in required_fields:
                if field not in data:
                    self._send_error(f"Missing required field: {field}", 400)
                    return
            self._handle_create_playlist(data)
        else:
            self._send_error("Unknown action", 400)

    def _handle_get_auth_url(self):
        """Generate Spotify authorization URL"""
        try:
            client_id = os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
            redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
            
            # If no redirect URI in env, determine from request headers
            if not redirect_uri:
                # Try to get the origin from the request
                origin = self.headers.get('Origin', '')
                referer = self.headers.get('Referer', '')
                
                if origin and origin.startswith('https://'):
                    redirect_uri = origin + '/'
                elif referer and referer.startswith('https://'):
                    # Extract base URL from referer
                    from urllib.parse import urlparse
                    parsed = urlparse(referer)
                    redirect_uri = f"{parsed.scheme}://{parsed.netloc}/"
                else:
                    # Fallback to default
                    redirect_uri = "https://yoga-playlist-app.vercel.app/"
            
            print(f"[DEBUG] Using redirect URI: {redirect_uri}")
            print(f"[DEBUG] Origin header: {self.headers.get('Origin', 'None')}")
            print(f"[DEBUG] Referer header: {self.headers.get('Referer', 'None')}")
            
            if not client_id or not client_secret:
                response = {
                    "success": False,
                    "error": "Spotify credentials not configured"
                }
            else:
                scope = "playlist-modify-public playlist-modify-private"
                
                sp_oauth = SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope=scope,
                    cache_path=None,  # Don't cache in serverless
                    show_dialog=True  # Always show auth dialog
                )
                
                auth_url = sp_oauth.get_authorize_url()
                
                response = {
                    "success": True,
                    "auth_url": auth_url,
                    "message": "Please authorize with Spotify to create playlists"
                }
            
        except Exception as e:
            response = {
                "success": False,
                "error": f"Failed to generate auth URL: {str(e)}"
            }
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode())

    def _handle_create_playlist(self, data):
        """Create playlist with authorization code"""
        try:
            playlist_name = data['playlist_name']
            track_ids = data['track_ids']
            auth_code = data.get('auth_code')
            
            print(f"[DEBUG] Create playlist request - Name: {playlist_name}, Tracks: {len(track_ids)}, Has auth code: {bool(auth_code)}")
            
            if not auth_code:
                # No auth code - need to get authorization first
                print("[DEBUG] No auth code provided, requesting authorization")
                response = {
                    "success": False,
                    "needs_auth": True,
                    "message": "Spotify authorization required. Please authorize first."
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Create playlist with auth code
            client_id = os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
            redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
            
            # If no redirect URI in env, determine from request headers (same logic as auth URL)
            if not redirect_uri:
                origin = self.headers.get('Origin', '')
                referer = self.headers.get('Referer', '')
                
                if origin and origin.startswith('https://'):
                    redirect_uri = origin + '/'
                elif referer and referer.startswith('https://'):
                    from urllib.parse import urlparse
                    parsed = urlparse(referer)
                    redirect_uri = f"{parsed.scheme}://{parsed.netloc}/"
                else:
                    redirect_uri = "https://yoga-playlist-app.vercel.app/"
            
            print(f"[DEBUG] Token exchange using redirect URI: {redirect_uri}")
            
            sp_oauth = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope="playlist-modify-public playlist-modify-private",
                cache_path=None
            )
            
            # Get access token from auth code
            print(f"[DEBUG] Attempting to get access token with auth code: {auth_code[:10]}...")
            try:
                token_info = sp_oauth.get_access_token(auth_code)
                print(f"[DEBUG] Token info received: {bool(token_info)}")
            except Exception as token_error:
                print(f"[ERROR] Failed to get access token: {str(token_error)}")
                self._send_error(f"Failed to get access token: {str(token_error)}", 400)
                return
            
            if not token_info:
                print("[ERROR] Token info is None")
                self._send_error("Failed to get access token", 400)
                return
            
            # Create Spotify client with access token
            sp = spotipy.Spotify(auth=token_info['access_token'])
            
            # Get user info
            user_info = sp.current_user()
            user_id = user_info['id']
            
            # Create playlist
            playlist = sp.user_playlist_create(
                user=user_id,
                name=playlist_name,
                description="Generated by Yoga Playlist AI",
                public=False
            )
            
            # Add tracks to playlist
            if track_ids and len(track_ids) > 0:
                # Spotify API accepts max 100 tracks at once
                for i in range(0, len(track_ids), 100):
                    batch = track_ids[i:i+100]
                    sp.playlist_add_items(playlist['id'], batch)
            
            response = {
                "success": True,
                "message": f"✅ Created playlist '{playlist_name}' with {len(track_ids)} tracks",
                "playlist_created": True,
                "playlist_url": playlist['external_urls']['spotify'],
                "playlist_id": playlist['id']
            }
            
        except Exception as e:
            self._send_error(f"Failed to create playlist: {str(e)}", 500)
            return
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode())

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