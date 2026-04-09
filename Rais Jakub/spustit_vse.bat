@echo off
cd /d "%~dp0"

pip install flask

:: Hra se spusti v novem okne
start "Hledani min" python game.py

:: Flask spustime na pozadi
start /b python highscore_web.py

:: Pockat 2 sekundy nez Flask nabehne, pak otevrit defaultni prohlizec
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5000

echo.
echo Vse bezi bez problemu.
pause
