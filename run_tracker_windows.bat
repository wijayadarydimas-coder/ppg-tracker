@echo off
REM Script untuk setup environment variables dan test PPG Tracker di Windows

echo.
echo ================================================================================
echo PPG TRACKER - Windows Setup
echo ================================================================================
echo.

REM Set environment variables
set EMAIL_SENDER=darydimas32@gmail.com
set EMAIL_PASSWORD=your_app_password_here
set EMAIL_RECIPIENT=darydimas32@gmail.com

echo.
echo ============= ENVIRONMENT VARIABLES =============
echo EMAIL_SENDER: %EMAIL_SENDER%
echo EMAIL_PASSWORD: [hidden]
echo EMAIL_RECIPIENT: %EMAIL_RECIPIENT%
echo.

REM Check if Playwright is installed
python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo ❌ Playwright belum terinstall!
    echo.
    echo Installing Playwright...
    pip install playwright beautifulsoup4 --break-system-packages
    echo.
    echo Installing Chrome browser...
    playwright install chromium
    echo ✅ Playwright installed!
) else (
    echo ✅ Playwright sudah terinstall
)

echo.
echo =================== MENJALANKAN TEST ===================
echo.
python ppg_tracker_playwright.py

pause
