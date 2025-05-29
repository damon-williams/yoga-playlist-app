from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.coordinator import CoordinatorAgent
from agents.music_integration import MusicIntegrationAgent
from tools.spotify_tool import SpotifyTool

app = Flask(__name__)
CORS(app)

# Initialize agents (will be done lazily)
coordinator = None
music_integration = None

def get_coordinator():
    global coordinator
    if coordinator is None:
        coordinator = CoordinatorAgent()
    return coordinator

def get_music_integration():
    global music_integration
    if music_integration is None:
        music_integration = MusicIntegrationAgent()
    return music_integration

@app.route('/')
def home():
    return jsonify({"message": "Yoga Playlist API is running!", "status": "healthy"})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agents_initialized": coordinator is not None,
        "timestamp": "2024-01-01T00:00:00Z"
    })

@app.route('/api/classes', methods=['GET'])
def get_classes():
    """Get all available yoga class types"""
    try:
        coord = get_coordinator()
        classes_text = coord.list_available_classes()
        
        # Parse the text response - handle numbered lists
        classes = []
        lines = classes_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered list items (1., 2., 3.) OR bullet points (•)
            if (line and (line[0].isdigit() or line.startswith('•'))):
                # Remove the number/bullet and clean up
                if line[0].isdigit():
                    # Handle numbered format: "1. Name: Description"
                    content = line.split('.', 1)[1].strip() if '.' in line else line
                else:
                    # Handle bullet format: "• Name: Description"
                    content = line[1:].strip()
                
                if ':' in content:
                    name, description = content.split(':', 1)
                    classes.append({
                        "name": name.strip(),
                        "description": description.strip()
                    })
        
        return jsonify({
            "success": True,
            "classes": classes,
            "total": len(classes)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/classes', methods=['POST'])
def add_class():
    """Add a new yoga class type"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        name = data['name'].strip()
        description = data['description'].strip()
        
        if not name or not description:
            return jsonify({
                "success": False,
                "error": "Name and description cannot be empty"
            }), 400
        
        # Use the class storage tool to add the class
        from tools.class_storage_tool import ClassStorageTool
        class_storage = ClassStorageTool()
        
        # Add to database
        result = class_storage._add_class_type(
            name=name,
            description=description,
            typical_duration=data.get('duration'),
            energy_level=data.get('energy_level'),
            music_style_notes=data.get('music_style_notes')
        )
        
        return jsonify({
            "success": True,
            "message": result,
            "class": {
                "name": name,
                "description": description
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate-playlist', methods=['POST'])
def generate_playlist():
    """Generate a complete playlist using the agent system"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['class_name', 'music_preferences', 'duration']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        class_name = data['class_name']
        music_preferences = data['music_preferences']
        duration = int(data['duration'])
        
        # Generate playlist directly with music curator
        coord = get_coordinator()
        music_int = get_music_integration()
        
        # Create a simple class description
        class_info = f"{class_name} class ({duration} minutes)"
        
        # Generate playlist using music curation agent directly
        playlist = coord.music_curator.recommend_music(
            class_info=class_info,
            music_preferences=music_preferences,
            duration_minutes=duration
        )
        
        # Process with music integration to find Spotify tracks
        playlist_result = music_int.process_full_playlist(
            class_name=class_name,
            playlist_text=playlist
        )
        
        # Combine results
        response = {
            "success": True,
            "playlist": playlist,
            "spotify_integration": playlist_result,
            "ready_for_export": playlist_result.get("ready_for_spotify", False)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/create-spotify-playlist', methods=['POST'])
def create_spotify_playlist():
    """Create actual Spotify playlist"""
    try:
        data = request.get_json()
        
        required_fields = ['playlist_name', 'track_ids']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        playlist_name = data['playlist_name']
        track_ids = data['track_ids']
        description = data.get('description', 'Generated by Yoga Playlist AI')
        
        # Create playlist using Spotify tool
        spotify_tool = SpotifyTool()
        result = spotify_tool.create_playlist(
            playlist_name=playlist_name,
            track_ids=track_ids,
            description=description
        )
        
        # Check if creation was successful
        if result.startswith("✅"):
            return jsonify({
                "success": True,
                "message": result,
                "playlist_created": True
            })
        else:
            return jsonify({
                "success": False,
                "error": result
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test-spotify', methods=['GET'])
def test_spotify():
    """Test Spotify connection"""
    try:
        spotify_tool = SpotifyTool()
        result = spotify_tool.run("action:test")
        
        if result.startswith("✅"):
            return jsonify({
                "success": True,
                "message": result,
                "connected": True
            })
        else:
            return jsonify({
                "success": False,
                "message": result,
                "connected": False
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "connected": False
        }), 500

# For Vercel serverless functions
def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True)