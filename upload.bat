@echo off
REM 进入项目目录
cd /d "E:\touxiangAI"

REM 检查当前状态
echo 检查 Git 状态...
git status

REM 添加所有修改的文件
echo 添加所有文件到暂存区...
git add .

REM 提交到本地仓库
echo 提交到本地仓库...
git commit -m "update project files: backend, frontend, scripts and docs"

REM 推送到远程仓库
echo 推送到 GitHub...
git push origin main

echo.
echo 操作完成！请检查上方输出确认是否成功。
pause