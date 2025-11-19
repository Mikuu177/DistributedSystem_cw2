@echo off
REM This script will run the load test for the air quality workflow.

REM Set the title of the window
TITLE Running Air Quality Load Test

REM Change directory to the script's location
cd /d "%~dp0"

echo.
echo ==================================================================
echo  Starting Air Quality Workflow Load Test
echo ==================================================================
echo.
echo Current Directory: %cd%
echo.

REM Check if python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not found in your system's PATH.
    echo Please install Python and make sure it is added to the PATH.
    pause
    exit /b
)

echo Found Python version:
python --version
echo.

REM Run the load test script
echo Starting load_test.py... Please wait, this may take 15-20 minutes.
echo.

python load_test.py

REM Check if the script ran successfully
if %errorlevel% neq 0 (
    echo.
    echo ERROR: The load test script failed to complete.
    echo Please check the error messages above.
) else (
    echo.
    echo SUCCESS: The load test script completed successfully.
    echo The results have been saved to 'performance_results.csv'.
)

echo.
echo ==================================================================
echo  Test Finished
necho ==================================================================
echo.
pause

