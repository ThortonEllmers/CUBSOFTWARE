from flask import Flask, send_from_directory, render_template
import socket
import os
import sys
import importlib.util
from jinja2 import ChoiceLoader, FileSystemLoader

# Create the main Flask app with multiple template folders
app = Flask(__name__,
            static_folder='website/static')

# Configure Jinja to look in multiple template directories
app.jinja_loader = ChoiceLoader([
    FileSystemLoader('website'),
    FileSystemLoader('website/includes'),
    FileSystemLoader('apps/music-downloader/templates'),
    FileSystemLoader('apps/social-media-saver/templates')
])

# ==================== MAIN WEBSITE ROUTES ====================

@app.route('/')
def index():
    """Serve the main landing page"""
    return render_template('index.html')

@app.route('/terms')
def terms():
    """Serve the terms of use page"""
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    """Serve the privacy policy page"""
    return render_template('privacy.html')

@app.route('/copyright')
def copyright_claims():
    """Serve the copyright claims page"""
    return render_template('copyright.html')

@app.route('/contact')
def contact():
    """Serve the contact page"""
    return render_template('contact.html')

@app.route('/static/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files for main website"""
    return send_from_directory('website/static/css', filename)

@app.route('/static/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files for main website"""
    return send_from_directory('website/static/js', filename)

@app.route('/static/images/<path:filename>')
def serve_images(filename):
    """Serve image files for main website"""
    return send_from_directory('website/static/images', filename)

@app.route('/api/stats')
def get_combined_stats():
    """Get combined stats from all apps"""
    from flask import jsonify
    total = 0

    # Get music downloader stats
    try:
        total += music_module.total_downloads
    except:
        pass

    # Get social media saver stats
    try:
        total += social_module.total_downloads
    except:
        pass

    return jsonify({'total_downloads': total})

# ==================== MUSIC DOWNLOADER APP INTEGRATION ====================

# Load Music Downloader blueprint using importlib
music_blueprint_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apps', 'music-downloader', 'app_blueprint.py')
spec_music = importlib.util.spec_from_file_location("music_blueprint", music_blueprint_path)
music_module = importlib.util.module_from_spec(spec_music)
spec_music.loader.exec_module(music_module)
app.register_blueprint(music_module.youtube_bp, url_prefix='/apps/music-downloader')

# ==================== SOCIAL MEDIA SAVER APP INTEGRATION ====================

# Load Social Media Saver blueprint using importlib
social_blueprint_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apps', 'social-media-saver', 'app_blueprint.py')
spec_social = importlib.util.spec_from_file_location("social_blueprint", social_blueprint_path)
social_module = importlib.util.module_from_spec(spec_social)
spec_social.loader.exec_module(social_module)
app.register_blueprint(social_module.social_media_bp, url_prefix='/apps/social-media-saver')

# ==================== SERVER STARTUP ====================

if __name__ == '__main__':
    # Get local IP
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "192.168.1.27"

    print("=" * 70)
    print("                       CUB SOFTWARE")
    print("=" * 70)
    print()
    print("Main Landing Page:")
    print(f"  • Local:       http://localhost:3000")
    print(f"  • Network:     http://{local_ip}:3000")
    print(f"  • Your IP:     http://192.168.1.27:3000")
    print()
    print("Music Downloader App:")
    print(f"  • Local:       http://localhost:3000/apps/music-downloader")
    print(f"  • Network:     http://{local_ip}:3000/apps/music-downloader")
    print(f"  • Your IP:     http://192.168.1.27:3000/apps/music-downloader")
    print()
    print("Social Media Saver App:")
    print(f"  • Local:       http://localhost:3000/apps/social-media-saver")
    print(f"  • Network:     http://{local_ip}:3000/apps/social-media-saver")
    print(f"  • Your IP:     http://192.168.1.27:3000/apps/social-media-saver")
    print()
    print("=" * 70)
    print("Server running on all network interfaces (0.0.0.0:3000)")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    # Run the server
    app.run(host='0.0.0.0', port=3000, debug=False, threaded=True)
