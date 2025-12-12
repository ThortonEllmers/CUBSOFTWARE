import yt_dlp
import os
import sys
import subprocess

def is_spotify_url(url):
    """Check if URL is from Spotify"""
    return 'spotify.com' in url

def download_spotify(url, output_path='downloads', quality='320'):
    """Download from Spotify using spotdl"""
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    try:
        print(f"Processing Spotify URL: {url}\n")

        # Check for YouTube cookies file
        cookies_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'youtube_cookies.txt')

        # Use system spotdl (works on both Windows and Linux)
        cmd = ["spotdl", url, "--output", output_path, "--format", "mp3", "--bitrate", f"{quality}k"]

        # Add cookies if available (spotdl uses yt-dlp internally)
        if os.path.exists(cookies_file):
            cmd.extend(["--cookie-file", cookies_file])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print("\nSpotify download complete!")
            return True
        else:
            print(f"\nError downloading from Spotify")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def download_mp3(url, output_path='downloads', quality='320'):
    """
    Download YouTube video or playlist as MP3 at specified quality

    Args:
        url: YouTube video or playlist URL
        output_path: Directory to save the MP3 files
        quality: Audio quality in kbps (128, 192, 256, or 320)
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Clean up URL - remove radio/autoplay playlist parameters
    # Only keep explicit playlist parameter
    import re
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        # Remove radio/autoplay parameters
        if 'list' in params:
            # Check if it's a radio playlist (starts with RD)
            if params['list'][0].startswith('RD'):
                print("Detected radio playlist, downloading only the requested video...")
                del params['list']
                if 'start_radio' in params:
                    del params['start_radio']
                # Rebuild URL
                new_query = urlencode(params, doseq=True)
                url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    except:
        pass  # If URL parsing fails, continue with original URL

    # FFmpeg will be auto-detected from system PATH on Linux, or use Windows path if exists
    ffmpeg_path = None
    if os.name == 'nt':  # Windows
        windows_ffmpeg = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages', 'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe', 'ffmpeg-8.0.1-full_build', 'bin')
        if os.path.exists(windows_ffmpeg):
            ffmpeg_path = windows_ffmpeg

    # Check for YouTube cookies file
    cookies_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'youtube_cookies.txt')

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
        ],
        'ffmpeg_location': ffmpeg_path if ffmpeg_path else None,
        'cookiefile': cookies_file if os.path.exists(cookies_file) else None,
        'extractor_args': {
            'youtube': {
                'player_client': ['web'],
            }
        },
        'remote_components': ['ejs:github'],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,  # Continue on download errors in playlists
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Processing: {url}\n")
            # Just download directly - yt-dlp will handle playlists automatically
            ydl.download([url])
            print(f"\nDownload complete!")
            return True
    except Exception as e:
        print(f"Error downloading: {e}")
        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Download audio from YouTube or Spotify')
    parser.add_argument('url', help='URL to download')
    parser.add_argument('--quality', default='320', choices=['128', '192', '256', '320'],
                       help='Audio quality in kbps (default: 320)')

    args = parser.parse_args()

    url = args.url
    quality = args.quality

    # Route to appropriate downloader based on URL
    if is_spotify_url(url):
        download_spotify(url, quality=quality)
    else:
        download_mp3(url, quality=quality)
