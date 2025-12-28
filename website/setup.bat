@echo off
echo Setting up ASL Connect Website...

:: Create virtual environment
python -m venv asl_env
echo Virtual environment created.

:: Activate virtual environment
call asl_env\Scripts\activate

:: Install requirements
pip install -r requirements.txt
echo Requirements installed.

:: Check project structure
python check_structure.py

echo Setup completed!
echo.
echo To run the website:
echo 1. Activate virtual environment: asl_env\Scripts\activate
echo 2. Run: python app.py
echo 3. Open: http://localhost:5000
pause