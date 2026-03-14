# RefundPilot Start Script
# Usage: powershell -ExecutionPolicy Bypass -File start.ps1
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "[RefundPilot] Fresh Start" -ForegroundColor Cyan
Write-Host "================================"
Write-Host "[1/5] Killing old processes..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort 5174 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Start-Sleep 2
Write-Host "[2/5] Deleting old database..." -ForegroundColor Yellow
Remove-Item "$root\backend\refundpilot.db" -Force -ErrorAction SilentlyContinue
Write-Host "[3/5] Patching frontend rollup..." -ForegroundColor Yellow
Set-Location "$root\frontend"
node patch-rollup.cjs 2>$null
Write-Host "[4/5] Starting backend on port 8001..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m","uvicorn","main:app","--port","8001" -WorkingDirectory "$root\backend"
Start-Sleep 4
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -ErrorAction Stop
    Write-Host "  Backend OK: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "  Backend may still be starting..." -ForegroundColor Yellow
}
Write-Host "[5/5] Starting frontend on port 5173..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "cmd" -ArgumentList "/c","cd","$root\frontend","&&","npx","vite","--port","5173" -WorkingDirectory "$root\frontend"
Start-Sleep 3
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "RefundPilot is running!" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8001"
Write-Host "  Frontend: http://localhost:5173"
Write-Host "  Demo:     http://localhost:5173/demo"
Write-Host ""
