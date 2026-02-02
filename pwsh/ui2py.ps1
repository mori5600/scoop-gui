$root   = Split-Path $PSScriptRoot -Parent
$uiDir  = Join-Path $root "app/ui"
$outDir = Join-Path $root "app/ui_generated"

if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

Get-ChildItem -Path $uiDir -Filter *.ui | ForEach-Object {
    $outPath = Join-Path $outDir ("ui_" + $_.BaseName + ".py")
    pyside6-uic $_.FullName -o $outPath
    Write-Host "Generated $outPath"
}

ruff check $outDir --fix && ruff format $outDir
