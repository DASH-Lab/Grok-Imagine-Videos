@echo off
echo ========================================
echo Grok Video Generation Pipeline
echo ========================================
echo.

echo Step 1: Generating prompts...
python prompt_gen.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to generate prompts!
    echo Please check the error above.
    pause
    exit /b 1
)

echo.
echo Step 2: Creating videos from prompts...
python video_create.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to create videos!
    echo Please check the error above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Pipeline completed successfully!
echo ========================================
pause