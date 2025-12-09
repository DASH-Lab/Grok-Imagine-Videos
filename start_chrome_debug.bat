@echo off
echo Starting Chrome with Remote Debugging...
echo.
echo IMPORTANT: Close ALL other Chrome windows first!
echo.
timeout /t 3 /nobreak >nul
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug" --disable-dev-shm-usage
echo.
echo Chrome is now running with automation support on port 9222

echo You can close this window
pause

