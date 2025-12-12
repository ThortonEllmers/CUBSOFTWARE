let activeDownloads = new Map();
let pollInterval = null;

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
    setTimeout(() => {
        errorDiv.classList.remove('show');
    }, 5000);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Add to page
    document.body.appendChild(notification);

    // Trigger animation
    setTimeout(() => notification.classList.add('show'), 10);

    // Remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function isValidUrl(url) {
    const validDomains = ['youtube.com', 'youtu.be', 'spotify.com', 'music.youtube.com'];
    return validDomains.some(domain => url.includes(domain));
}

async function startDownload() {
    const urlInput = document.getElementById('urlInput');
    const qualitySelect = document.getElementById('qualitySelect');
    const downloadBtn = document.getElementById('downloadBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');

    const url = urlInput.value.trim();
    const quality = qualitySelect.value;

    if (!url) {
        showError('Please enter a URL');
        return;
    }

    if (!isValidUrl(url)) {
        showError('Invalid URL. Only YouTube and Spotify URLs are supported');
        return;
    }

    // Disable button
    downloadBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'block';

    try {
        const response = await fetch('/apps/music-downloader/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url, quality })
        });

        const data = await response.json();

        if (response.ok) {
            // Clear input
            urlInput.value = '';

            // Add to active downloads
            activeDownloads.set(data.task_id, {
                url: url,
                status: 'queued'
            });

            // Start polling if not already running
            if (!pollInterval) {
                startPolling();
            }

            // Update UI immediately
            updateDownloadsUI();
        } else {
            showError(data.error || 'Failed to start download');
        }
    } catch (error) {
        showError('Network error. Please try again.');
        console.error('Download error:', error);
    } finally {
        // Re-enable button
        downloadBtn.disabled = false;
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
    }
}

function startPolling() {
    pollInterval = setInterval(async () => {
        if (activeDownloads.size === 0) {
            clearInterval(pollInterval);
            pollInterval = null;
            return;
        }

        for (const [taskId, download] of activeDownloads.entries()) {
            try {
                const response = await fetch(`/apps/music-downloader/api/status/${taskId}`);
                if (response.ok) {
                    const data = await response.json();

                    // Check if download just completed
                    const wasCompleted = download.status === 'completed';
                    const isNowCompleted = data.status === 'completed' && !wasCompleted;

                    activeDownloads.set(taskId, data);

                    // Auto-download files as they become available
                    // Check for new files that haven't been downloaded yet
                    if (data.files && data.files.length > 0) {
                        const previousFiles = new Set(download.files || []);
                        const newFiles = data.files.filter(file => !previousFiles.has(file));

                        if (newFiles.length > 0) {
                            console.log('New files available:', newFiles);

                            // Download new files immediately
                            newFiles.forEach((file, index) => {
                                setTimeout(() => {
                                    console.log('Triggering download for:', file);
                                    const filename = file.split('/').pop();
                                    showNotification(`Downloading: ${filename}`, 'success');
                                    downloadFile(file);
                                }, index * 500); // 500ms delay between each
                            });
                        }
                    }

                    // Show final completion notification
                    if (isNowCompleted) {
                        const fileCount = data.files.length;
                        const message = fileCount === 1
                            ? 'Download complete!'
                            : `All ${fileCount} files downloaded!`;
                        showNotification(message, 'success');
                    }

                    // Remove completed or failed downloads after 2 minutes
                    if ((data.status === 'completed' || data.status === 'failed') &&
                        !download.removeTimeout) {
                        download.removeTimeout = setTimeout(() => {
                            // Fade out animation
                            const card = document.getElementById(`download-${taskId}`);
                            if (card) {
                                card.style.opacity = '0';
                                card.style.transform = 'translateY(-10px)';
                                setTimeout(() => {
                                    activeDownloads.delete(taskId);
                                    updateDownloadsUI();
                                }, 300);
                            } else {
                                activeDownloads.delete(taskId);
                                updateDownloadsUI();
                            }
                        }, 120000); // 2 minutes
                    }
                } else if (response.status === 404) {
                    // Task not found on server, remove from activeDownloads
                    console.log(`Task ${taskId} not found on server, removing from UI`);
                    activeDownloads.delete(taskId);
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        }

        updateDownloadsUI();
    }, 2000); // Poll every 2 seconds
}

function updateDownloadsUI() {
    const container = document.getElementById('activeDownloads');

    if (activeDownloads.size === 0) {
        container.innerHTML = '';
        return;
    }

    // Update existing cards instead of replacing everything
    const existingCards = new Set();

    for (const [taskId, download] of activeDownloads.entries()) {
        existingCards.add(taskId);

        let card = document.getElementById(`download-${taskId}`);

        if (card) {
            // Update existing card content
            const statusBadge = card.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = `status-badge status-${download.status}`;
                statusBadge.textContent = download.status.charAt(0).toUpperCase() + download.status.slice(1);
            }

            const progressFill = card.querySelector('.progress-fill');
            if (progressFill) {
                progressFill.style.width = `${download.progress || 0}%`;
            }

            // Update title if available
            const titleElement = card.querySelector('.download-title');
            const urlSmallElement = card.querySelector('.download-url-small');
            if (titleElement && download.title) {
                titleElement.textContent = download.title;
                titleElement.title = download.title;
                // Add small URL if not already there
                if (!urlSmallElement) {
                    const titleSection = card.querySelector('.download-title-section');
                    if (titleSection) {
                        const urlDiv = document.createElement('div');
                        urlDiv.className = 'download-url-small';
                        urlDiv.textContent = download.url;
                        urlDiv.title = download.url;
                        titleSection.appendChild(urlDiv);
                    }
                }
            }

            // Update logs section
            const logsSection = card.querySelector('.logs-section');
            if (logsSection && download.logs && download.logs.length > 0) {
                logsSection.innerHTML = download.logs.slice(-15).map(log =>
                    `<div class="log-line">${escapeHtml(log)}</div>`
                ).join('');
                // Auto-scroll to bottom
                logsSection.scrollTop = logsSection.scrollHeight;
            }

            // Update files section if download completed
            if (download.status === 'completed' && download.files && download.files.length > 0) {
                const existingFiles = card.querySelector('.download-files');
                if (!existingFiles) {
                    const filesHTML = `
                        <div class="download-files">
                            <h4>Downloaded (${download.files.length} file${download.files.length > 1 ? 's' : ''}):</h4>
                            <div class="file-list">
                                ${download.files.map(file => `
                                    <div class="file-item">
                                        <span class="file-name" title="${file}">✅ ${file}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                    card.insertAdjacentHTML('beforeend', filesHTML);
                }
            }
        } else {
            // Create new card
            card = createDownloadCard(taskId, download);
            container.appendChild(card);
        }
    }

    // Remove cards that no longer exist in activeDownloads
    const allCards = container.querySelectorAll('.download-card');
    allCards.forEach(card => {
        const taskId = card.id.replace('download-', '');
        if (!existingCards.has(taskId)) {
            card.remove();
        }
    });
}

function createDownloadCard(taskId, download) {
    const card = document.createElement('div');
    card.className = 'download-card';
    card.id = `download-${taskId}`;

    const statusClass = `status-${download.status}`;
    const statusText = download.status.charAt(0).toUpperCase() + download.status.slice(1);

    // Display title or URL with playlist info
    let displayTitle = download.title || download.url;
    let playlistInfo = '';

    if (download.playlist_count > 1) {
        playlistInfo = `<span class="playlist-badge">${download.files.length}/${download.playlist_count} songs</span>`;
        if (!download.title || download.title.includes('http')) {
            displayTitle = `Playlist Download`;
        }
    }

    const isUrl = !download.title || download.title.includes('http');

    let filesHTML = '';
    if (download.files && download.files.length > 0) {
        filesHTML = `
            <div class="download-files">
                <h4>Downloaded (${download.files.length} file${download.files.length > 1 ? 's' : ''}):</h4>
                <div class="file-list">
                    ${download.files.map(file => `
                        <div class="file-item">
                            <span class="file-name" title="${file}">✅ ${file}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Always show logs section for active downloads
    let logsHTML = '';
    if (download.status === 'downloading' || download.status === 'queued' ||
        (download.logs && download.logs.length > 0)) {
        const logs = download.logs && download.logs.length > 0
            ? download.logs.slice(-15).map(log => `<div class="log-line">${escapeHtml(log)}</div>`).join('')
            : '<div class="log-line">Initializing download...</div>';
        logsHTML = `
            <div class="logs-section">
                ${logs}
            </div>
        `;
    }

    let errorHTML = '';
    if (download.error) {
        errorHTML = `<div class="error-message show">${escapeHtml(download.error)}</div>`;
    }

    // Add cancel button for active downloads
    const cancelButtonHTML = (download.status === 'downloading' || download.status === 'queued') ? `
        <button class="cancel-btn" onclick="cancelDownload('${taskId}')">Cancel</button>
    ` : '';

    card.innerHTML = `
        <div class="download-header">
            <div class="download-title-section">
                <div class="download-title" title="${escapeHtml(displayTitle)}">
                    ${escapeHtml(displayTitle)} ${playlistInfo}
                </div>
                ${isUrl ? '' : `<div class="download-url-small" title="${escapeHtml(download.url)}">${escapeHtml(download.url)}</div>`}
            </div>
            <div class="download-actions">
                ${cancelButtonHTML}
                <span class="status-badge ${statusClass}">${statusText}</span>
            </div>
        </div>
        ${download.status === 'downloading' || download.status === 'queued' ? `
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${download.progress || 0}%"></div>
            </div>
        ` : ''}
        ${errorHTML}
        ${filesHTML}
        ${logsHTML}
    `;

    return card;
}

async function cancelDownload(taskId) {
    if (!confirm('Are you sure you want to cancel this download?')) {
        return;
    }

    try {
        const response = await fetch(`/apps/music-downloader/api/cancel/${taskId}`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            if (activeDownloads.has(taskId)) {
                const download = activeDownloads.get(taskId);
                download.status = 'cancelled';
                updateDownloadsUI();
            }
        } else {
            const data = await response.json();
            showError(data.error || 'Failed to cancel download');
        }
    } catch (error) {
        showError('Network error. Failed to cancel download.');
        console.error('Cancel error:', error);
    }
}

function downloadFile(filename) {
    console.log('downloadFile called with:', filename);
    // Create a temporary anchor element to trigger download
    const a = document.createElement('a');
    a.href = `/apps/music-downloader/download/${encodeURIComponent(filename)}`;
    // Get just the filename, handling both forward and backslashes
    a.download = filename.split(/[/\\]/).pop();
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    console.log('Download triggered for:', filename);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load existing downloads when page loads
async function loadExistingDownloads() {
    try {
        const response = await fetch('/apps/music-downloader/api/downloads');
        if (response.ok) {
            const downloads = await response.json();

            // Add all active downloads to the map
            downloads.forEach(download => {
                if (download.status !== 'completed' && download.status !== 'failed') {
                    activeDownloads.set(download.task_id, download);
                }
            });

            // Start polling if there are active downloads
            if (activeDownloads.size > 0) {
                updateDownloadsUI();
                startPolling();
            }
        }
    } catch (error) {
        console.error('Failed to load existing downloads:', error);
    }
}

// Format number with k, M, B suffixes
function formatNumber(num) {
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + 'B';
    }
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    }
    return num.toString();
}

// Poll for stats updates
async function updateStats() {
    try {
        const response = await fetch('/apps/music-downloader/api/stats');
        if (response.ok) {
            const stats = await response.json();
            const totalElement = document.getElementById('totalDownloads');
            const actualElement = document.getElementById('totalDownloadsActual');
            if (totalElement) {
                totalElement.textContent = formatNumber(stats.total_downloads);
            }
            if (actualElement) {
                actualElement.textContent = '(' + stats.total_downloads.toLocaleString() + ')';
            }
        }
    } catch (error) {
        console.error('Stats update error:', error);
    }
}

// Allow Enter key to submit and load existing downloads on page load
document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('urlInput');
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            startDownload();
        }
    });

    // Load any existing downloads
    loadExistingDownloads();

    // Start polling for stats every 2 seconds
    updateStats();
    setInterval(updateStats, 2000);
});
