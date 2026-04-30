@echo off
chcp 65001 > nul
echo ========================================
echo   PhotoArt Desktop Build Script
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Clear old build files...
if exist dist\PhotoArtDesktop rmdir /s /q dist\PhotoArtDesktop
if exist build\PhotoArtDesktop rmdir /s /q build\PhotoArtDesktop

echo [2/3] Run PyInstaller build...
python -m PyInstaller PhotoArtDesktop.spec -y

echo [3/3] Done!
echo.
echo Build complete! Output: dist\PhotoArtDesktop
echo.
pause