import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from langchain.tools import BaseTool
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class SpotifyTool(BaseTool):
    name = "spotify_search"
    description = "Search for tracks on Spotify and create playlists"
    
    def __init__(self):
        super().__init__()
    
    def _get_spotify_client(self):
        """Initialize Spotify client with OAuth"""
        try:
            scope = "playlist-modify-public playlist-modify-private"
            auth_manager = SpotifyOAuth(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                scope=scope,
                cache_path=".spotify_cache"
            )
            return spotipy.Spotify(auth_manager=auth_manager)
        except Exception as e:
            print(f"❌ Spotify authentication failed: {e}")
            return None
    
    def _run(self, query: str) -> str:
        """
        Query format: "action:search,track:Artist - Song" or "action:create_playlist,name:Playlist Name"
        """
        sp = self._get_spotify_client()
        if not sp:
            return "❌ Spotify not authenticated. Check your credentials."
        
        try:
            # Parse query
            params = {}
            for part in query.split(','):
                if ':' in part:
                    key, value = part.split(':', 1)
                    params[key.strip()] = value.strip()
            
            action = params.get('action', 'search')
            
            if action == "search":
                return self._search_track(params.get('track', ''), sp)
            elif action == "test":
                return self._test_connection(sp)
            else:
                return f"Unknown action: {action}. Use 'search' or 'test'"
                
        except Exception as e:
            return f"Spotify error: {str(e)}"
    
    def _search_track(self, search_query: str, sp) -> str:
        """Search for a specific track on Spotify"""
        if not search_query:
            return "❌ No search query provided"
        
        try:
            results = sp.search(q=search_query, type='track', limit=5)
            tracks = results['tracks']['items']
            
            if not tracks:
                return f"❌ No tracks found for: {search_query}"
            
            # Format results
            found_tracks = []
            for track in tracks:
                artist_names = ", ".join([artist['name'] for artist in track['artists']])
                duration_ms = track['duration_ms']
                duration_min = f"{duration_ms // 60000}:{(duration_ms % 60000) // 1000:02d}"
                
                found_tracks.append(
                    f"• {artist_names} - {track['name']} ({duration_min}) | Spotify ID: {track['id']}"
                )
            
            return f"🎵 Found tracks for '{search_query}':\n" + "\n".join(found_tracks)
            
        except Exception as e:
            return f"❌ Search failed: {str(e)}"
    
    def _test_connection(self, sp) -> str:
        """Test Spotify connection"""
        try:
            user_info = sp.current_user()
            return f"✅ Connected to Spotify as: {user_info['display_name']} ({user_info['id']})"
        except Exception as e:
            return f"❌ Connection test failed: {str(e)}"
    
    def search_multiple_tracks(self, track_list: List[str]) -> Dict[str, Dict]:
        """Search for multiple tracks and return structured data"""
        results = {}
        sp = self._get_spotify_client()
        
        if not sp:
            return {"error": "Spotify client not available"}
        
        for track_query in track_list:
            try:
                search_results = sp.search(q=track_query, type='track', limit=1)
                tracks = search_results['tracks']['items']
                
                if tracks:
                    track = tracks[0]
                    results[track_query] = {
                        'found': True,
                        'spotify_id': track['id'],
                        'name': track['name'],
                        'artists': [artist['name'] for artist in track['artists']],
                        'duration_ms': track['duration_ms'],
                        'preview_url': track['preview_url']
                    }
                else:
                    results[track_query] = {
                        'found': False,
                        'error': 'Track not found'
                    }
            except Exception as e:
                results[track_query] = {
                    'found': False,
                    'error': str(e)
                }
        
        return results
    
    def create_playlist(self, playlist_name: str, track_ids: List[str], 
                      description: str = "Generated by Yoga Playlist AI") -> str:
        """Create a Spotify playlist with given tracks"""
        sp = self._get_spotify_client()
        if not sp:
            return "❌ Spotify client not available"
            
        try:
            user_id = sp.current_user()['id']
            
            # Create playlist
            playlist = sp.user_playlist_create(
                user=user_id,
                name=playlist_name,
                description=description,
                public=False
            )
            
            # Add tracks to playlist
            if track_ids:
                sp.playlist_add_items(playlist['id'], track_ids)
            
            return f"✅ Created playlist '{playlist_name}' with {len(track_ids)} tracks: {playlist['external_urls']['spotify']}"
            
        except Exception as e:
            return f"❌ Failed to create playlist: {str(e)}"


# Test the Spotify tool
if __name__ == "__main__":
    print("=== Testing Spotify Tool ===")
    
    tool = SpotifyTool()
    
    # Test 1: Connection test
    print("\n1. Testing Spotify connection:")
    result = tool.run("action:test")
    print(result)
    
    # Test 2: Search for a track
    print("\n2. Searching for a hip-hop track:")
    result = tool.run("action:search,track:Tupac California Love")
    print(result)
    
    # Test 3: Search for trip-hop
    print("\n3. Searching for trip-hop:")
    result = tool.run("action:search,track:Massive Attack Teardrop")
    print(result)