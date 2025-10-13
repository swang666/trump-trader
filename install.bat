@echo off
echo ===============================================
echo Trump Truth Social Trading Monitor - Setup
echo ===============================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Downloading spaCy language model...
python -m spacy download en_core_web_sm

echo.
echo ===============================================
echo Installation complete!
echo ===============================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Get FREE Gemini API key: https://makersuite.google.com/app/apikey
echo 3. Add your API key to .env (optional but recommended)
echo 4. Run: python test_gemini.py (to test API)
echo 5. Run: python test_system.py (to test system)
echo 6. Run: python main.py (to start monitoring)
echo.
pause

