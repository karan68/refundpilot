# RefundPilot — Fresh Start Script (Windows PowerShell)
# Deletes old DB, kills old processes, starts backend + frontend
# Usage: .\start.ps1

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "🤖 RefundPilot — Fresh Start" -ForegroundColor Cyan
Write-Host "================================"

# Kill old processes on ports 8001 and 5173
Write-Host "🔄 Killing old processes..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort 5174 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Start-Sleep 2

# Delete old database
Write-Host "🗑️  Deleting old database..." -ForegroundColor Yellow
Remove-Item "$root\backend\refundpilot.db" -Force -ErrorAction SilentlyContinue

# Patch frontend rollup
Write-Host "🔧 Patching frontend..." -ForegroundColor Yellow
Set-Location "$root\frontend"
node patch-rollup.cjs 2>$null

# Start backend in background
Write-Host "🚀 Starting backend on port 8001..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m","uvicorn","main:app","--port","8001" -WorkingDirectory "$root\backend"

Start-Sleep 4

# Check backend health
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -ErrorAction Stop
    Write-Host "✅ Backend running: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend may still be starting... wait a few seconds" -ForegroundColor Yellow
}

# Start frontend in background
Write-Host "🎨 Starting frontend on port 5173..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "npx" -ArgumentList "vite","--port","5173" -WorkingDirectory "$root\frontend"

Start-Sleep 3

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ RefundPilot is running!" -ForegroundColor Green
Write-Host "   Backend:  http://localhost:8001"
Write-Host "   Frontend: http://localhost:5173"
Write-Host "   API Docs: http://localhost:8001/docs"
Write-Host "   Demo:     http://localhost:5173/demo"
Write-Host ""
Write-Host "To stop: close this terminal or run:" -ForegroundColor Gray
Write-Host "  Get-NetTCPConnection -LocalPort 8001,5173 | ForEach-Object { Stop-Process -Id `$_.OwningProcess -Force }" -ForegroundColor Gray
