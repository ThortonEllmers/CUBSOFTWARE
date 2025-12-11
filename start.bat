@echo off
cls
echo ======================================================================
echo                    CUB SOFTWARE - SERVER STARTING
echo ======================================================================
echo.
echo Starting all applications from one location...
echo Binding to: 0.0.0.0:3000 (accessible from all network interfaces)
echo Your local IP: 192.168.1.27:3000
echo.
echo ======================================================================
echo.

REM Start the main server
"C:\Users\Thorton\AppData\Local\Programs\Python\Python312\python.exe" main.py

echo.
echo Server stopped.
pause
