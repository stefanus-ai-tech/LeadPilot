param([string]$Destination = 'C:\Users\DELL\Documents\LocalLLM')
$ErrorActionPreference = 'Stop'
$sourceRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$destinationRoot = [System.IO.Path]::GetFullPath($Destination)
if ($sourceRoot.TrimEnd('\') -eq $destinationRoot.TrimEnd('\')) {
    throw 'The project is already in the destination folder. Follow README.md to set it up.'
}
$items = @('app', 'tests', 'samples', 'requirements.txt', 'pytest.ini', 'README.md', 'smoke_test.py', '.gitignore', 'VALIDATION.md')
foreach ($item in $items) {
    if (Test-Path -LiteralPath (Join-Path $destinationRoot $item)) {
        throw "Destination already contains $item. No files were copied; inspect it first."
    }
}
New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null
foreach ($item in $items) {
    $sourceItem = Join-Path $sourceRoot $item
    if (Test-Path -LiteralPath $sourceItem -PathType Container) {
        $targetFolder = Join-Path $destinationRoot $item
        New-Item -ItemType Directory -Path $targetFolder -Force | Out-Null
        Get-ChildItem -LiteralPath $sourceItem -File | ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination $targetFolder
        }
    } else {
        Copy-Item -LiteralPath $sourceItem -Destination $destinationRoot
    }
}
Write-Host "Source files copied to $destinationRoot."
Write-Host 'Follow README.md to create a new .venv, install dependencies, run pytest, and start the API.'
