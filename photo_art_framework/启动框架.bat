@echo off
chcp 65001 >nul
color 0B

echo.
echo ================================================
echo.
echo      写真/艺术照训练框架 v2.0
echo      (预处理 + 训练 + 图片生成)
echo.
echo ================================================
echo.
echo  按 Ctrl+C 停止服务
echo.
echo ================================================
echo.

cd /d "%~dp0"
python main.py
pause
