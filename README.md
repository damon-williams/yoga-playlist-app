# 🧘‍♀️ Yoga Playlist Generator

An AI-powered web application that creates personalized Spotify playlists for yoga classes using LangChain and OpenAI.

## 🌟 Features

- **AI-Powered Playlist Generation**: Uses OpenAI GPT to create structured playlists based on class type and music preferences
- **Real Spotify Integration**: Searches Spotify for actual tracks and creates playlists in user accounts
- **Dynamic Class Management**: Add custom yoga class types with descriptions stored in Supabase
- **Responsive Design**: Clean, modern interface that works on desktop and mobile
- **OAuth Flow**: Secure Spotify authentication for playlist creation
- **Share Functionality**: Easy sharing options to help other yoga teachers discover the app

## 🚀 Live Demo

Visit the app at: [https://yoga-playlist-app.vercel.app/](https://yoga-playlist-app.vercel.app/)

## 🛠️ Tech Stack

### Frontend
- **HTML/CSS/JavaScript**: Vanilla web technologies for maximum performance
- **Responsive Design**: Mobile-first approach with modern CSS

### Backend
- **Vercel Serverless Functions**: Python-based API endpoints
- **LangChain + OpenAI**: AI playlist generation
- **Supabase**: PostgreSQL database for yoga class types
- **Spotify Web API**: Music search and playlist creation

### APIs & Services
- **OpenAI GPT-3.5**: Natural language playlist generation
- **Spotify Web API**: Music search and playlist management
- **Supabase**: Database and real-time features
- **PostHog**: Analytics and user tracking

## 📁 Project Structure

```
├── api/                      # Vercel serverless functions
│   ├── health.py            # Health check endpoint
│   ├── classes.py           # Yoga class management
│   ├── generate-playlist.py # AI playlist generation + Spotify search
│   ├── create-spotify-playlist.py # Spotify playlist creation
│   └── test-spotify.py      # Spotify connection testing
├── web/                     # Frontend files
│   ├── index.html          # Main application page
│   ├── css/
│   │   └── main.css        # Styles and responsive design
│   └── js/
│       └── app.js          # Application logic and API calls
├── requirements.txt         # Python dependencies
├── vercel.json             # Vercel deployment configuration
└── README.md               # This file
```

## 🔧 Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js (for Vercel CLI)
- Spotify Developer Account
- OpenAI API Key
- Supabase Account

### Environment Variables

Create the following environment variables in your Vercel project:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Spotify
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=https://your-domain.com/

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# PostHog (optional)
POSTHOG_API_KEY=your_posthog_key
```

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd yoga-playlist-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

4. **Set up environment variables**
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add SPOTIFY_CLIENT_ID
   # ... add all other environment variables
   ```

5. **Run locally**
   ```bash
   vercel dev
   ```

### Deployment

Deploy to Vercel:
```bash
vercel --prod
```

## 🎵 How It Works

1. **Class Selection**: Users select from pre-defined yoga class types or add custom ones
2. **Preferences Input**: Optional music style and preferences input
3. **AI Generation**: LangChain + OpenAI generates a structured playlist with specific songs
4. **Spotify Search**: App searches Spotify for each generated track
5. **Playlist Creation**: Users authenticate with Spotify and the app creates the playlist
6. **Success & Sharing**: Users can open their playlist and share the app

## 🔐 Spotify Setup

1. Create a Spotify app at [developer.spotify.com](https://developer.spotify.com/)
2. Add your redirect URI (e.g., `https://your-domain.com/`)
3. Note your Client ID and Client Secret
4. Add them to your environment variables

## 🗄️ Database Schema

### Yoga Classes Table (Supabase)
```sql
CREATE TABLE yoga_classes (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for the powerful GPT models
- **Spotify** for their comprehensive Web API
- **Supabase** for the excellent backend-as-a-service
- **Vercel** for seamless deployment
- **LangChain** for AI application framework

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🌟 Future Features

- [ ] Music mood analysis and BPM detection
- [ ] Playlist collaboration features
- [ ] Integration with other music services (Apple Music, YouTube Music)
- [ ] Advanced AI agents for music curation quality control
- [ ] Playlist templates and sharing
- [ ] Mobile app version

---

Made with ❤️ for yoga teachers and music lovers