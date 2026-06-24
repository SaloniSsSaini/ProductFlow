# Bootstrap local development environment for ProductFlow (Windows).
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot

Write-Host "==> ProductFlow setup"

$EnvFile = Join-Path $RootDir ".env"
$EnvExample = Join-Path $RootDir ".env.example"
if (-not (Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "Created .env from .env.example"
}

Write-Host "==> Backend virtual environment"
python -m venv (Join-Path $RootDir ".venv")
& (Join-Path $RootDir ".venv\Scripts\Activate.ps1")
python -m pip install --upgrade pip
pip install -r (Join-Path $RootDir "backend\requirements.txt")

Write-Host "==> Frontend dependencies"
Set-Location (Join-Path $RootDir "frontend")
npm install

Write-Host ""
Write-Host "Setup complete."
Write-Host "  Backend:  .venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --app-dir backend"
Write-Host "  Frontend: cd frontend; npm run dev"
