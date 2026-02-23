# start_app.ps1 - Launch Intercede backend + frontend concurrently
# Run from the repo root: .\start_app.ps1

$root = $PSScriptRoot

Write-Host "Starting Intercede..." -ForegroundColor Cyan

# ── Backend ─────────────────────────────────────────────────────────────────
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "& { `$host.UI.RawUI.WindowTitle = 'Intercede - Backend'; " +
    "cd '$root\backend'; " +
    "Write-Host 'Backend starting on http://localhost:8000' -ForegroundColor Green; " +
    "uvicorn app:app --reload --port 8000 }"
)

# ── Frontend ─────────────────────────────────────────────────────────────────
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "& { `$host.UI.RawUI.WindowTitle = 'Intercede - Frontend'; " +
    "cd '$root\frontend'; " +
    "Write-Host 'Frontend starting on http://localhost:5173' -ForegroundColor Green; " +
    "npm run dev }"
)

Write-Host ""
Write-Host "  Backend  -> http://localhost:8000" -ForegroundColor Yellow
Write-Host "  Frontend -> http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "Both processes are running in separate windows." -ForegroundColor Cyan
