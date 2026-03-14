# RefundPilot — Fresh Start Script (Windows PowerShell)
# Deletes old DB, kills old processes, starts backend + frontend
# Usage: .\start.ps1

Write-Host "🤖 RefundPilot — Fresh Start" -ForegroundColor Cyan
Write-Host "================================"

# Kill old processes on ports 8001 and 5173
Write-Host "🔄 Killing old processes..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Start-Sleep 2

# Delete old database
Write-Host "🗑️  Deleting old database..." -ForegroundColor Yellow
Remove-Item "$PSScriptRoot\backend\refundpilot.db" -Force -ErrorAction SilentlyContinue

# Start backend
Write-Host "🚀 Starting backend on port 8001..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot\backend
    python -m uvicorn main:app --port 8001
}

Start-Sleep 4

# Check backend health
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -ErrorAction Stop
    Write-Host "✅ Backend running: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend may still be starting..." -ForegroundColor Yellow
}

# Start frontend
Write-Host "🎨 Starting frontend..." -ForegroundColor Green
Set-Location "$PSScriptRoot\frontend"
node patch-rollup.cjs 2>$null
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot\frontend
    npx vite --port 5173
}

Start-Sleep 3

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ RefundPilot is running!" -ForegroundColor Green
Write-Host "   Backend:  http://localhost:8001"
Write-Host "   Frontend: http://localhost:5173"
Write-Host "   API Docs: http://localhost:8001/docs"
Write-Host "   Demo:     http://localhost:5173/demo"
Write-Host ""
Write-Host "Press Ctrl+C to stop. Run 'Get-Job | Stop-Job' to clean up." -ForegroundColor Gray

# Wait for user interrupt
try {
    while ($true) {
        Start-Sleep 5
        # Check if jobs are still running
        if ($backendJob.State -ne 'Running') {
            Write-Host "⚠️  Backend stopped. Restarting..." -ForegroundColor Yellow
            Receive-Job $backendJob
        }
    }
} finally {
    Write-Host "`n🛑 Stopping servers..." -ForegroundColor Red
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
}
