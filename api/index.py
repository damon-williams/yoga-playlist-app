from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
@app.route('/api')
def home():
    return {"message": "Yoga Playlist API is running!", "status": "healthy"}

@app.route('/api/health')
def health_check():
    return {"status": "healthy", "message": "API is working"}

@app.route('/api/test')
def test():
    return {"test": "success", "message": "Basic API endpoint working"}

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda *args: None)

# For local testing
if __name__ == '__main__':
    app.run(debug=True)