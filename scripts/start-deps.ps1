# 启动 docker-compose 中的 PostgreSQL + Redis（仓库根目录）
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) {
    Write-Host "未在 PATH 中找到 docker。请安装 Docker Desktop 并确保 `docker compose` 可用，"
    Write-Host "或在本机自行安装 PostgreSQL（5432）与 Redis（6379），并编辑 backend/.env 中的连接串。"
    exit 0
}
docker compose up -d
Write-Host "已执行 docker compose up -d。数据库: localhost:5432 aurashift/aurashift；Redis: localhost:6379"
