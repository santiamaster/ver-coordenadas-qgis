param(
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pluginSource = Join-Path $repoRoot "ver_coordenadas"
$distDir = Join-Path $repoRoot "dist"
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

New-Item -ItemType Directory -Path $distDir -Force | Out-Null

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

# Se construye el ZIP mediante ZipArchive para garantizar que las rutas internas
# usen "/" como separador, tal como requiere el formato ZIP y esperan los
# entornos multiplataforma (Windows, Linux y macOS).
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$zipStream = [System.IO.File]::Open(
    $zipPath,
    [System.IO.FileMode]::CreateNew,
    [System.IO.FileAccess]::ReadWrite,
    [System.IO.FileShare]::None
)
$archive = New-Object System.IO.Compression.ZipArchive(
    $zipStream,
    [System.IO.Compression.ZipArchiveMode]::Create,
    $false
)

try {
    foreach ($file in $files) {
        $sourcePath = Join-Path $pluginSource $file
        $entryName = "ver_coordenadas/" + $file

        $entry = $archive.CreateEntry(
            $entryName,
            [System.IO.Compression.CompressionLevel]::Optimal
        )

        $entryStream = $entry.Open()
        $sourceStream = [System.IO.File]::OpenRead($sourcePath)

        try {
            $sourceStream.CopyTo($entryStream)
        }
        finally {
            $sourceStream.Dispose()
            $entryStream.Dispose()
        }
    }
}
finally {
    $archive.Dispose()
    $zipStream.Dispose()
}

$archive = [System.IO.Compression.ZipFile]::OpenRead($zipPath)

try {
    $entries = $archive.Entries | ForEach-Object { $_.FullName }

    $expectedEntries = $files | ForEach-Object { "ver_coordenadas/" + $_ }

    $missing = $expectedEntries | Where-Object { $_ -notin $entries }
    $unexpected = $entries | Where-Object { $_ -notin $expectedEntries }
    $nonPortable = $entries | Where-Object { $_ -match "\\" }

    if ($missing.Count -gt 0) {
        throw "El ZIP no contiene: $($missing -join ', ')"
    }

    if ($unexpected.Count -gt 0) {
        throw "El ZIP contiene archivos inesperados: $($unexpected -join ', ')"
    }

    if ($nonPortable.Count -gt 0) {
        throw "El ZIP contiene rutas no portables con barra invertida: $($nonPortable -join ', ')"
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
