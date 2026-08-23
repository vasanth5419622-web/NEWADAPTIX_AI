# PowerShell Launcher for ADAPTIX-FARM
Write-Host "========================================================" -ForegroundColor Green
Write-Host "Starting ADAPTIX-FARM Agricultural Intelligence Server" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green

$RootPath = Resolve-Path "$PSScriptRoot\.."
$env:PYTHONPATH = "$RootPath\backend"

Set-Location $RootPath
python backend\app\main.py
