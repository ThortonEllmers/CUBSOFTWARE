# CUBS Song Downloader

🎵 A beautiful web-based music downloader that extracts audio at the highest quality (320kbps). Supports YouTube, YouTube Music, and Spotify.

## ✨ Features

- **🌐 Web Interface** - Easy-to-use website accessible from any device
- **320kbps MP3** - Highest quality audio
- **📱 Responsive Design** - Works on desktop, tablet, and mobile
- **⚡ Real-time Progress** - Live download status and logs
- **🎨 Modern UI** - Beautiful gradient design with smooth animations
- **📦 Batch Downloads** - Queue multiple URLs
- **🎵 Full Metadata** - Proper ID3 tags, artist, title, album artwork
- **🔄 Multi-source Support:**
  - YouTube videos
  - YouTube playlists
  - YouTube Music
  - Spotify tracks
  - Spotify playlists
- **🚀 Easy Deployment** - Deploy to DigitalOcean in minutes

## 🚀 Quick Start

### Local Testing (Windows)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
start_web.bat
```

3. Open your browser:
```
http://localhost:3000
```

### Local Testing (Linux/Mac)

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Make the start script executable and run:
```bash
chmod +x start_web.sh
./start_web.sh
```

3. Open your browser:
```
http://localhost:3000
```

## 🌐 Deploy to DigitalOcean

See [DEPLOYMENT.md](DEPLOYMENT.md) for a complete guide on deploying to DigitalOcean VPS.

Quick summary:
1. Create Ubuntu 22.04 droplet
2. Install dependencies (Python, FFmpeg, Nginx)
3. Upload files and setup virtual environment
4. Configure systemd service
5. Configure Nginx reverse proxy
6. Access via your domain or IP

## 📋 Requirements

- Python 3.8 or later
- FFmpeg (for audio conversion)
- yt-dlp (for YouTube)
- spotdl (for Spotify)
- Flask (web framework)

**All automatically installed via requirements.txt!**

## 🎯 How to Use

1. Open the website in your browser
2. Paste a YouTube or Spotify URL
3. Click "Download"
4. Wait for processing to complete
5. Download your MP3 file(s)

**Supported URLs:**
- YouTube: `https://www.youtube.com/watch?v=...`
- YouTube Playlist: `https://www.youtube.com/playlist?list=...`
- YouTube Music: `https://music.youtube.com/...`
- Spotify Track: `https://open.spotify.com/track/...`
- Spotify Playlist: `https://open.spotify.com/playlist/...`

## 📁 Project Structure

```
cubs-song-downloader/
├── app.py              # Flask web application
├── downloader.py       # Core download logic
├── templates/          # HTML templates
│   └── index.html
├── static/            # CSS and JavaScript
│   ├── style.css
│   └── script.js
├── downloads/         # Downloaded MP3 files
├── requirements.txt   # Python dependencies
├── mp3cloud.service   # Systemd service file
├── nginx.conf         # Nginx configuration
└── DEPLOYMENT.md      # Deployment guide
```

## 🔧 Legacy CLI Usage

The original command-line interface is still available:

```bash
python downloader.py <URL>
```

Or use the GUI:
```bash
python gui.py
```

## 🛠️ Development

Run in development mode with auto-reload:
```bash
export FLASK_ENV=development
python app.py
```

## 📝 Output Format

- **Single tracks:** `downloads/Artist - Title.mp3`
- **Playlists:** `downloads/Playlist Name/Artist - Title.mp3`

All files include:
- 320kbps MP3 encoding
- Full ID3 metadata
- Embedded album artwork
- Organized folder structure

## 🤝 Credits

Made by CUB | [Discord Profile](https://discord.com/users/378501056008683530)

## 📄 License

For personal use only. Respect copyright laws and platform terms of service.
