param(
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pluginSource = Join-Path $repoRoot "ver_coordenadas"
$distDir = Join-Path $repoRoot "dist"
$stagingDir = Join-Path $distDir "staging"
$pluginStaging = Join-Path $stagingDir "ver_coordenadas"
$zipPath = Join-Path $distDir ("ver_coordenadas-" + $Version + ".zip")

$files = @(
    "__init__.py",
    "plugin.py",
    "geometry.py",
    "measurements.py",
    "formatter.py",
    "dialog.py",
    "warning.py",
    "metadata.txt",
    "LICENSE",
    "icon.png"
)

Write-Host "Construyendo Ver Coordenadas $Version..." -ForegroundColor Cyan

if (-not (Test-Path $pluginSource)) {
    throw "No se encontro la carpeta del plugin: $pluginSource"
}

foreach ($file in $files) {
    $sourcePath = Join-Path $pluginSource $file
    if (-not (Test-Path $sourcePath)) {
        throw "Falta un archivo obligatorio para el paquete: $sourcePath"
    }
}

if (Test-Path $stagingDir) {
    Remove-Item $stagingDir -Recurse -Force
}

New-Item -ItemType Directory -Path $pluginStaging -Force | Out-Null
New-Item -ItemType Directory -Path $distDir -Force | Out-Null

foreach ($file in $files) {
    Copy-Item (Join-Path $pluginSource $file) (Join-Path $pluginStaging $file)
}

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path $pluginStaging -DestinationPath $zipPath -CompressionLevel Optimal

Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($zipPath)

try {
    $entries = $archive.Entries | ForEach-Object { $_.FullName.Replace("\", "/") }

    $expectedEntries = $files | ForEach-Object { "ver_coordenadas/" + $_ }

    $missing = $expectedEntries | Where-Object { $_ -notin $entries }
    $unexpected = $entries | Where-Object {
        $_ -ne "ver_coordenadas/" -and $_ -notin $expectedEntries
    }

    if ($missing.Count -gt 0) {
        throw "El ZIP no contiene: $($missing -join ', ')"
    }

    if ($unexpected.Count -gt 0) {
        throw "El ZIP contiene archivos inesperados: $($unexpected -join ', ')"
    }

    Write-Host ""
    Write-Host "Contenido del ZIP:" -ForegroundColor Green
    $entries | Sort-Object | ForEach-Object { Write-Host "  $_" }
}
finally {
    $archive.Dispose()
}

$zipInfo = Get-Item $zipPath
$hash = Get-FileHash $zipPath -Algorithm SHA256

Write-Host ""
Write-Host "ZIP candidato creado correctamente." -ForegroundColor Green
Write-Host "Ruta: $($zipInfo.FullName)"
Write-Host "Tamano: $($zipInfo.Length) bytes"
Write-Host "SHA256: $($hash.Hash)"
