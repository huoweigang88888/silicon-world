@echo off
echo ========================================
echo 硅基世界 - 代码同步脚本
echo ========================================
echo.

cd /d %~dp0

echo [1/3] 添加更改...
git add -A

echo.
echo [2/3] 提交更改...
set /p message="输入提交信息： "
if "%message%"=="" set message=chore: 更新代码

git commit -m "%message%"

echo.
echo [3/3] 推送到 GitHub...
git push -u origin main

echo.
echo ========================================
echo 同步完成！
echo ========================================
pause
