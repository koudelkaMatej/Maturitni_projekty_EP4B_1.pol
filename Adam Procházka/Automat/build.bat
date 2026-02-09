@echo off
setlocal

cd /d "%~dp0"
echo Akt. slozka: %CD%
echo.

echo Mazani build a dist...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul

echo.
echo Kontrola slozek:
if not exist assets\ echo [CHYBA] assets\ neexistuje v %CD% & pause & exit /b 1
if not exist data\ echo [CHYBA] data\ neexistuje v %CD% & pause & exit /b 1
if not exist icon.ico echo [CHYBA] icon.ico neexistuje v %CD% & pause & exit /b 1

echo.
echo Spoustim PyInstaller...
py -m PyInstaller --noconfirm --clean --onedir --noconsole --name PixSpin --icon=icon.ico ^
 --add-data "assets/images;assets/images" ^
 --add-data "assets/fonts;assets/fonts" ^
 --add-data "data;data" ^
 automat.py

echo.
echo Kontrola vystupu:
set ASSETS_OK=0
if exist dist\PixSpin\assets\ set ASSETS_OK=1
if exist dist\PixSpin\_internal\assets\ set ASSETS_OK=1
if "%ASSETS_OK%"=="0" echo [CHYBA] assets se nezabalily ani do root ani do _internal. & pause & exit /b 1

set DATA_OK=0
if exist dist\PixSpin\data\ set DATA_OK=1
if exist dist\PixSpin\_internal\data\ set DATA_OK=1
if "%DATA_OK%"=="0" echo [CHYBA] data se nezabalila ani do root ani do _internal. & pause & exit /b 1

echo.
echo Hotovo! Spust: dist\PixSpin\PixSpin.exe
pause
endlocal
