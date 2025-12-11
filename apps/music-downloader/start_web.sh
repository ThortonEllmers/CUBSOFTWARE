#!/bin/bash

echo "Starting CUBS Song Downloader Web Server..."
echo ""
echo "Server will be accessible at:"
echo "  - Local:   http://localhost:3000"
echo "  - Network: http://$(hostname -I | awk '{print $1}'):3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
