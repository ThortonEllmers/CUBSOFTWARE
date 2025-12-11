"""
YouTube MP3 Downloader - Blueprint version for integration with main website
"""
from flask import Blueprint, render_template, request, jsonify, send_file, send_from_directory
import os
import uuid
import threading
import queue
import subprocess
import time

# Get absolute paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Create Blueprint with absolute paths
youtube_bp = Blueprint('youtube_mp3', __name__,
                      template_folder=os.path.join(APP_DIR, 'templates'),
                      static_folder=os.path.join(APP_DIR, 'static'),
                      static_url_path='/static')

# Configuration - use absolute paths
DOWNLOAD_FOLDER = os.path.join(APP_DIR, 'downloads')
TEMP_FOLDER = os.path.join(APP_DIR, 'temp_downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Global download queue and status tracking
download_queue = queue.Queue()
active_downloads = {}
download_history = []
total_downloads = 0  # Global stats counter

class DownloadTask:
    def __init__(self, task_id, url, quality='320'):
        self.task_id = task_id
        self.url = url
        self.quality = quality
        self.status = 'queued'
        self.progress = 0
        self.current_file = ''
        self.title = ''
        self.playlist_count = 0
        self.playlist_current = 0
        self.error = None
        self.files = []
        self.logs = []
        self.process = None

def process_downloads():
    """Background worker that processes the download queue"""
    while True:
        try:
            task = download_queue.get()
            if task is None:
                break

            task_id = task.task_id
            url = task.url
            active_downloads[task_id].status = 'downloading'

            # Create unique folder for this download
            download_path = os.path.join(TEMP_FOLDER, task_id)
            os.makedirs(download_path, exist_ok=True)

            try:
                # Run the downloader with quality parameter
                if os.name == 'nt':  # Windows
                    python_path = r"C:\Users\Thorton\AppData\Local\Programs\Python\Python312\python.exe"
                else:
                    python_path = 'python3'

                downloader_path = os.path.join(APP_DIR, 'downloader.py')

                # Track files before download
                files_before = set()
                if os.path.exists(DOWNLOAD_FOLDER):
                    for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
                        for file in files:
                            if file.endswith('.mp3'):
                                files_before.add(os.path.join(root, file))

                files_sent = set()

                process = subprocess.Popen(
                    [python_path, downloader_path, url, '--quality', task.quality],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    cwd=os.path.dirname(__file__)
                )

                active_downloads[task_id].process = process

                def check_for_new_files():
                    """Check for newly completed files"""
                    if os.path.exists(DOWNLOAD_FOLDER):
                        for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
                            for file in files:
                                if file.endswith('.mp3'):
                                    full_path = os.path.join(root, file)
                                    if full_path not in files_before and full_path not in files_sent:
                                        rel_path = os.path.relpath(full_path, DOWNLOAD_FOLDER)
                                        if rel_path not in active_downloads[task_id].files:
                                            active_downloads[task_id].files.append(rel_path)
                                            files_sent.add(full_path)
                                            if active_downloads[task_id].playlist_count > 1:
                                                completed = len(active_downloads[task_id].files)
                                                total = active_downloads[task_id].playlist_count
                                                active_downloads[task_id].title = f"Playlist ({completed}/{total} ready)"
                                            active_downloads[task_id].logs.append(f"✅ Ready: {rel_path}")

                for line in process.stdout:
                    if active_downloads[task_id].status == 'cancelled':
                        process.terminate()
                        break

                    log_line = line.rstrip()
                    active_downloads[task_id].logs.append(log_line)

                    # Parse playlist info
                    if '[download] Downloading item' in log_line or 'Downloading video' in log_line:
                        try:
                            import re
                            match = re.search(r'(\d+)\s+of\s+(\d+)', log_line)
                            if match:
                                current = int(match.group(1))
                                total = int(match.group(2))
                                active_downloads[task_id].playlist_current = current
                                active_downloads[task_id].playlist_count = total
                                if total > 1:
                                    active_downloads[task_id].title = f"Playlist ({current}/{total})"
                        except:
                            pass

                    # Extract title
                    if active_downloads[task_id].playlist_count <= 1:
                        if '[download] Destination:' in log_line:
                            try:
                                title = log_line.split('[download] Destination:')[-1].strip()
                                title = os.path.splitext(os.path.basename(title))[0]
                                active_downloads[task_id].title = title
                            except:
                                pass

                    if len(active_downloads[task_id].logs) > 100:
                        active_downloads[task_id].logs.pop(0)

                    if "Download complete" in log_line or "complete!" in log_line.lower():
                        active_downloads[task_id].progress = 100

                    check_for_new_files()

                process.wait()
                check_for_new_files()

                if process.returncode == 0:
                    files_after = set()
                    downloaded_files = []

                    if os.path.exists(DOWNLOAD_FOLDER):
                        for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
                            for file in files:
                                if file.endswith('.mp3'):
                                    full_path = os.path.join(root, file)
                                    files_after.add(full_path)

                    new_files = files_after - files_before

                    for file_path in new_files:
                        rel_path = os.path.relpath(file_path, DOWNLOAD_FOLDER)
                        downloaded_files.append(rel_path)

                    # Merge with existing files
                    for file in downloaded_files:
                        if file not in active_downloads[task_id].files:
                            active_downloads[task_id].files.append(file)

                    active_downloads[task_id].status = 'completed'
                    active_downloads[task_id].progress = 100

                    # Increment global stats
                    global total_downloads
                    total_downloads += len(downloaded_files) if downloaded_files else 1

                    if not active_downloads[task_id].title and downloaded_files:
                        try:
                            first_file = downloaded_files[0]
                            title = os.path.splitext(os.path.basename(first_file))[0]
                            active_downloads[task_id].title = title
                        except:
                            pass

                    if not downloaded_files:
                        active_downloads[task_id].logs.append("Warning: No new files detected")
                elif active_downloads[task_id].status == 'cancelled':
                    # Clean up partial files
                    if os.path.exists(DOWNLOAD_FOLDER):
                        for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
                            for file in files:
                                full_path = os.path.join(root, file)
                                if full_path not in files_before:
                                    try:
                                        os.remove(full_path)
                                        print(f"Cleaned up partial file: {file}")
                                    except Exception as e:
                                        print(f"Error cleaning up {file}: {e}")
                else:
                    active_downloads[task_id].status = 'failed'
                    active_downloads[task_id].error = 'Download failed'

            except Exception as e:
                active_downloads[task_id].status = 'failed'
                active_downloads[task_id].error = str(e)
                active_downloads[task_id].logs.append(f"Error: {str(e)}")

            download_history.append(task_id)

        except Exception as e:
            print(f"Worker error: {e}")
        finally:
            download_queue.task_done()

# Start background worker
worker_thread = threading.Thread(target=process_downloads, daemon=True)
worker_thread.start()

# Routes
@youtube_bp.route('/')
def index():
    return render_template('youtube_app.html')

@youtube_bp.route('/api/download', methods=['POST'])
def start_download():
    data = request.json
    url = data.get('url', '').strip()
    quality = data.get('quality', '320')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    if quality not in ['128', '192', '256', '320']:
        quality = '320'

    if not any(domain in url for domain in ['youtube.com', 'youtu.be', 'spotify.com', 'music.youtube.com']):
        return jsonify({'error': 'Invalid URL. Only YouTube and Spotify URLs are supported'}), 400

    task_id = str(uuid.uuid4())
    task = DownloadTask(task_id, url, quality)
    active_downloads[task_id] = task
    download_queue.put(task)

    return jsonify({
        'task_id': task_id,
        'status': 'queued',
        'message': 'Download queued successfully',
        'quality': quality
    })

@youtube_bp.route('/api/status/<task_id>')
def get_status(task_id):
    if task_id not in active_downloads:
        return jsonify({'error': 'Task not found'}), 404

    task = active_downloads[task_id]
    return jsonify({
        'task_id': task_id,
        'status': task.status,
        'progress': task.progress,
        'current_file': task.current_file,
        'title': task.title,
        'playlist_count': task.playlist_count,
        'playlist_current': task.playlist_current,
        'files': task.files,
        'logs': task.logs[-20:],
        'error': task.error
    })

@youtube_bp.route('/api/cancel/<task_id>', methods=['POST'])
def cancel_download(task_id):
    if task_id not in active_downloads:
        return jsonify({'error': 'Task not found'}), 404

    task = active_downloads[task_id]

    if task.status in ['completed', 'failed', 'cancelled']:
        return jsonify({'error': 'Cannot cancel a completed/failed/cancelled download'}), 400

    task.status = 'cancelled'
    task.error = 'Cancelled by user'

    if task.process:
        try:
            task.process.terminate()
        except:
            pass

    return jsonify({
        'task_id': task_id,
        'status': 'cancelled',
        'message': 'Download cancelled successfully'
    })

@youtube_bp.route('/api/downloads')
def list_downloads():
    downloads = []
    for task_id, task in active_downloads.items():
        downloads.append({
            'task_id': task_id,
            'url': task.url,
            'status': task.status,
            'progress': task.progress,
            'files': task.files
        })
    return jsonify(downloads)

@youtube_bp.route('/api/stats')
def get_stats():
    return jsonify({
        'total_downloads': total_downloads
    })

@youtube_bp.route('/download/<path:filename>')
def download_file(filename):
    try:
        # Prevent path traversal attacks
        file_path = os.path.abspath(os.path.join(DOWNLOAD_FOLDER, filename))
        download_folder_abs = os.path.abspath(DOWNLOAD_FOLDER)

        if not file_path.startswith(download_folder_abs + os.sep) and file_path != download_folder_abs:
            return jsonify({'error': 'Invalid file path'}), 403

        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def cleanup_old_files():
    """Background task to clean up files older than 30 seconds"""
    while True:
        try:
            cutoff_time = time.time() - 30  # 30 seconds ago

            if os.path.exists(DOWNLOAD_FOLDER):
                for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            if os.path.getmtime(file_path) < cutoff_time:
                                os.remove(file_path)
                                print(f"Cleaned up old file: {file}")
                        except Exception as e:
                            print(f"Error cleaning up {file}: {e}")

                # Remove empty directories
                for root, dirs, files in os.walk(DOWNLOAD_FOLDER, topdown=False):
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        try:
                            if not os.listdir(dir_path):
                                os.rmdir(dir_path)
                                print(f"Removed empty directory: {dir_name}")
                        except Exception as e:
                            pass
        except Exception as e:
            print(f"Cleanup error: {e}")

        time.sleep(15)  # Wait 15 seconds before next cleanup

# Start cleanup worker
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()
