@echo off
REM Inicia Artemis en http://127.0.0.1:7860
REM Uso: doble-click o desde PowerShell: .\iniciar-artemis.bat

cd /d "%~dp0"

echo Iniciando Artemis...
start "" http://127.0.0.1:7860
.venv\Scripts\python -m src.ui.app
