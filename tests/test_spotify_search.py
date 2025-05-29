import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.spotify_tool import SpotifyTool

# Test individual track search
tool = SpotifyTool()

print("=== Testing Individual Track Search ===")

# Test 1: Direct search via _run method
print("\n1. Testing direct search via _run:")
result = tool.run("action:search,track:Tupac California Love")
print(result)

# Test 2: Test search_multiple_tracks method
print("\n2. Testing search_multiple_tracks method:")
tracks = ["Tupac - California Love", "Biggie - Juicy"]
results = tool.search_multiple_tracks(tracks)
print(f"Results: {results}")

# Test 3: Test with exact search
print("\n3. Testing manual Spotify search:")
sp = tool._get_spotify_client()
if sp:
    try:
        manual_result = sp.search(q="Tupac California Love", type='track', limit=1)
        print(f"Manual search result: {len(manual_result['tracks']['items'])} tracks found")
        if manual_result['tracks']['items']:
            track = manual_result['tracks']['items'][0]
            print(f"First track: {track['artists'][0]['name']} - {track['name']}")
    except Exception as e:
        print(f"Manual search error: {e}")