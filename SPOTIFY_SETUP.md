# Spotify App Configuration Checklist

To ensure Spotify OAuth works correctly, please verify these settings in your Spotify App Dashboard:

## 1. Access Your Spotify App
1. Go to https://developer.spotify.com/dashboard
2. Log in and select your app

## 2. Verify Redirect URIs
In your app settings, make sure you have the following redirect URI added:
```
https://yoga-playlist-app.vercel.app/
```

**Important**: The redirect URI must match EXACTLY, including:
- The protocol (https://)
- The domain (yoga-playlist-app.vercel.app)
- The trailing slash (/)

## 3. Check Environment Variables
Ensure these are set in your Vercel dashboard:
- `SPOTIFY_CLIENT_ID` - Your app's client ID
- `SPOTIFY_CLIENT_SECRET` - Your app's client secret
- `SPOTIFY_REDIRECT_URI` - Should be `https://yoga-playlist-app.vercel.app/` (optional, defaults to this)

## 4. Common Issues
- **Invalid redirect URI**: The URI in Spotify app settings doesn't match exactly
- **Expired auth code**: Auth codes are only valid for a few minutes
- **Wrong environment**: Using development credentials in production

## 5. Testing the Fix
1. Clear your browser's localStorage: Run `localStorage.clear()` in console
2. Generate a new playlist
3. Try exporting to Spotify
4. Check browser console for debug messages