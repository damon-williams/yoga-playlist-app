# Yoga Playlist Generator

## Project Overview

An AI-powered web application that creates personalized Spotify playlists for yoga classes. Users input class type, preferences, and duration, and the app uses OpenAI to generate a structured playlist, then searches Spotify for actual tracks and creates playlists in user accounts.

## Architecture

### Frontend
- **Vanilla HTML/CSS/JavaScript**: Modern responsive design
- **PostHog Analytics**: User tracking and behavior analysis  
- **Spotify OAuth**: Authentication for playlist creation

### Backend (Vercel Serverless)
- **Python API endpoints**: `/api/generate-playlist`, `/api/create-spotify-playlist`
- **LangChain + OpenAI**: AI playlist generation using GPT-3.5
- **Supabase**: PostgreSQL database for yoga class types
- **Spotify Web API**: Music search and playlist creation

### Key Files
- `web/index.html`: Main application interface
- `web/js/app.js`: Frontend logic and API integration
- `api/generate-playlist.py`: AI playlist generation endpoint (💰 **COSTS MONEY**)
- `api/create-spotify-playlist.py`: Spotify integration

## Current User Flow

1. **Class Selection**: Choose yoga class type from dropdown
2. **Preferences**: Optional music style input  
3. **Duration**: Set class length (30-90 minutes)
4. **Generate**: Click "Generate Playlist" → calls `/api/generate-playlist` → **USES OPENAI (COSTS MONEY)**
5. **Review**: See generated playlist with Spotify track matches
6. **Export**: Authenticate with Spotify and create playlist

## Integration Opportunity: fairydust SDK

The playlist generation step uses OpenAI API calls which cost money. This is perfect for fairydust integration:

### Proposed Integration Points

1. **Replace "Generate Playlist" button** with fairydust Button component
2. **Add fairydust Account Component** to show user's DUST balance
3. **Charge DUST for playlist generation** instead of free API calls
4. **Set reasonable DUST pricing**: 
   - 5 DUST for basic playlist (30-60 min)
   - 8 DUST for extended playlist (75-90 min)

### Benefits
- **Monetize AI costs**: Cover OpenAI API expenses
- **User value**: Transparent pricing vs hidden costs
- **Sustainable business model**: Users pay for what they use
- **Enhanced UX**: fairydust authentication and balance management

## Technical Integration Plan

1. **Add fairydust SDK**: Include from CDN or npm
2. **Replace generate button**: Use fairydust Button component with DUST cost
3. **Add account widget**: Show user balance and connection status
4. **Update API flow**: 
   - Validate DUST transaction before OpenAI call
   - Consume DUST on successful generation
   - Handle insufficient balance gracefully

## Environment Variables

```bash
# Existing
OPENAI_API_KEY=your_openai_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# New for fairydust
FAIRYDUST_API_URL=https://your-fairydust-staging.railway.app
FAIRYDUST_APP_ID=your_registered_app_uuid
```

## Development Commands

```bash
# Local development
vercel dev

# Install dependencies  
pip install -r requirements.txt

# Deploy
vercel --prod
```

## Database Schema

### Existing: Supabase
```sql
CREATE TABLE yoga_classes (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Future: Usage Analytics
Could track DUST consumption patterns to optimize pricing and features.