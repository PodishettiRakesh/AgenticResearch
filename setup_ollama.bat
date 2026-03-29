@echo off
echo Setting up Ollama environment for AgenticResearch...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH. Please install Python first.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements from requirements_ollama.txt...
pip install -r requirements_ollama.txt

REM Check if Ollama is installed
ollama --version >nul 2>&1
if errorlevel 1 (
    echo Ollama is not installed. Please download and install it from https://ollama.ai/
    echo After installation, run this script again.
    pause
    exit /b 1
)

REM Ask user if they want to pull a model
set /p pull_model="Do you want to pull a model? (y/n): "
if /i "%pull_model%"=="y" (
    set /p model_name="Enter model name (e.g., llama2, mistral, codellama): "
    echo Pulling %model_name% model...
    ollama pull %model_name%
)

echo.
echo Setup complete!
echo.
echo To use Ollama:
echo 1. Make sure Ollama is running (ollama serve)
echo 2. Activate the virtual environment: .venv\Scripts\activate
echo 3. Run your Python scripts
echo.
pause
