# 在仓库根目录或任意位置执行：.\scripts\start-backend.ps1
# 依赖：backend\.venv 已安装 requirements.txt；PostgreSQL/Redis 见仓库根 docker-compose.yml
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
Set-Location $backend
if (-not (Test-Path ".\.venv\Scripts\uvicorn.exe")) {
    Write-Host "未找到 backend\.venv，请先: python -m venv .venv; .\.venv\Scripts\pip install -r requirements.txt"
    exit 1
}
$port = if ($env:BACKEND_PORT) { $env:BACKEND_PORT } else { "8000" }
Write-Host "启动 API: http://127.0.0.1:$port （环境变量 BACKEND_PORT 可改端口）"
& ".\.venv\Scripts\uvicorn.exe" app.main:app --reload --host 127.0.0.1 --port $port
