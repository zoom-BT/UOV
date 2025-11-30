@echo off
REM Script de démarrage rapide pour Windows

echo ========================================
echo Backend UOV Simplifié - Démarrage
echo ========================================
echo.

REM Installer les dépendances si nécessaire
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installation des dépendances...
    pip install -r requirements.txt
    echo.
)

echo Demarrage du serveur...
echo.
python app.py

pause
