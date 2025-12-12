# CUB SOFTWARE - cubsoftware.site

A unified platform hosting multiple web applications and tools, all accessible from one central location.

## 🌐 Website Structure

```
cubsoftware.site/
├── main.py                 # Main server that runs everything
├── start.bat              # Windows start script
├── start.sh               # Linux/Mac start script
├── requirements.txt       # All dependencies
├── website/               # Main landing page
│   ├── index.html
│   └── static/
│       ├── css/
│       └── js/
└── apps/                  # All applications
    └── youtube-mp3/       # YouTube to MP3 converter
        ├── app.py
        ├── downloader.py
        ├── templates/
        ├── static/
        └── downloads/
```

## 🚀 Quick Start

### **Option 1: Windows**

Double-click `start.bat` or run:
```batch
start.bat
```

### **Option 2: Linux/Mac**

```bash
chmod +x start.sh
./start.sh
```

### **Option 3: Manual Start**

```bash
# Windows
python main.py

# Linux/Mac
python3 main.py
```

## 📦 Installation

1. **Install Python 3.8+**

2. **Install FFmpeg** (required for YouTube MP3 app):
   - **Windows**: `winget install Gyan.FFmpeg`
   - **Linux**: `sudo apt install ffmpeg`
   - **Mac**: `brew install ffmpeg`

3. **Install Python dependencies**:
   ```bash
   pip install flask werkzeug yt-dlp spotdl
   ```

4. **Start the server**:
   ```bash
   python main.py
   ```

5. **Access the website**:
   - Main page: http://localhost:3000
   - YouTube MP3: http://localhost:3000/apps/youtube-mp3

## 🎯 How It Works

The main server (`main.py`) uses Flask with `DispatcherMiddleware` to:
- Serve the main landing page at the root URL
- Mount each app at its own URL path (`/apps/app-name`)
- Allow each app to run independently or as part of the main site

### **URLs:**
- **Main Landing Page**: `http://localhost:3000/`
- **YouTube MP3 App**: `http://localhost:3000/apps/youtube-mp3`
- *Future apps will be added at*: `http://localhost:3000/apps/app-name`

## 📱 Available Apps

### **1. YouTube to MP3 Downloader**
- **URL**: `/apps/youtube-mp3`
- **Features**:
  - Download from YouTube, YouTube Music, and Spotify
  - 320kbps MP3 quality
  - Full metadata and artwork
  - Playlist support
  - Real-time progress tracking

## ➕ Adding New Apps

1. **Create a new app folder**:
   ```
   apps/your-new-app/
   ├── app.py           # Flask app with routes
   ├── templates/       # HTML templates
   ├── static/          # CSS, JS, images
   └── requirements.txt # App-specific dependencies
   ```

2. **Update `main.py`** to import and mount your app:
   ```python
   from apps.your_new_app.app import app as new_app

   application = DispatcherMiddleware(main_app, {
       '/apps/youtube-mp3': youtube_mp3_app,
       '/apps/your-new-app': new_app  # Add this line
   })
   ```

3. **Add to landing page** (`website/index.html`):
   - Add a new app card with description and link
   - Update the CSS if needed

4. **Update requirements.txt** with any new dependencies

## 🔧 Configuration

### **Port Configuration**
Edit `main.py` line 55 to change the port:
```python
run_simple('0.0.0.0', 3000, application, ...)  # Change 3000 to your port
```

### **Production Deployment**
For production, use a proper WSGI server like Gunicorn:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:3000 main:application
```

Or use the provided deployment guides in each app's folder.

## 📁 Project Structure Details

### **Main Website** (`website/`)
- Static landing page with modern design
- Lists all available apps
- Responsive layout for mobile/desktop

### **Apps** (`apps/`)
- Each app is self-contained
- Can run standalone or integrated
- Has its own dependencies and configuration

### **Shared Resources**
- Python dependencies are combined in root `requirements.txt`
- Each app maintains its own data folders
- Apps don't share state or data

## 🛠️ Development

### **Running Apps Independently**
Each app can still run standalone:
```bash
cd apps/youtube-mp3
python app.py
```

### **Testing Changes**
1. Make changes to app code
2. Restart the main server
3. Test at `http://localhost:3000/apps/your-app`

### **Adding Static Files**
- **Main website**: `website/static/css/`, `website/static/js/`
- **App static files**: `apps/app-name/static/`

## 📝 Notes

- All apps run from ONE server on ONE port
- Apps are isolated from each other
- Easy to add, remove, or update apps
- Maintains original functionality when run standalone

## 🤝 Credits

Made by CUB | [Discord Profile](https://discord.com/users/378501056008683530)

## 📄 License

For personal use only. Respect copyright laws and platform terms of service.
