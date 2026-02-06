Write-Host "Checking code quality..." -ForegroundColor DarkGreen
Write-Host "Running ruff..." -ForegroundColor DarkGreen
ruff check app
Write-Host "Running ty..." -ForegroundColor DarkGreen
ty check app
Write-Host "Completed!" -ForegroundColor DarkGreen
