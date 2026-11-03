# Build and upload to PyPI. Run scripts/check.ps1 first.
# The version must not already exist on PyPI; credentials are supplied outside the repository.
$ErrorActionPreference = "Stop"

# Refuse dirty builds and check the version, not whether the project name already exists.
if (git status --porcelain) { throw "Commit the working tree before building a release." }
$projectText = Get-Content -LiteralPath (Join-Path $PSScriptRoot '../pyproject.toml') -Raw
$versionMatch = [regex]::Match($projectText, '(?m)^version = "([^"]+)"')
if (-not $versionMatch.Success) { throw "Cannot read the project version." }
$releaseVersion = $versionMatch.Groups[1].Value

# Works on both Windows PowerShell 5.1 and pwsh 7 (generic catch, no PS7-only types).
$taken = $true
try {
    Invoke-WebRequest -UseBasicParsing "https://pypi.org/pypi/stripcontrol/$releaseVersion/json" | Out-Null
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 404) { $taken = $false } else { throw }
}
if ($taken) { throw "stripcontrol $releaseVersion already exists on PyPI." }

$token = $env:PYPI_TOKEN
if (-not $token -and (Test-Path "C:\secrets\pypi-token.txt")) {
    $token = (Get-Content "C:\secrets\pypi-token.txt" -Raw).Trim()
}
if (-not $token) {
    throw "No PyPI token. Set `$env:PYPI_TOKEN or save it to C:\secrets\pypi-token.txt (never commit it)."
}

$output = Join-Path (Get-Location) ('dist/' + [guid]::NewGuid().ToString('N'))
python -m build --outdir $output
if ($LASTEXITCODE -ne 0) { throw "Build failed." }
python -m twine check --strict "$output/*"
if ($LASTEXITCODE -ne 0) { throw "Archive validation failed." }

$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = $token
try {
    python -m twine upload "$output/*"
    if ($LASTEXITCODE -ne 0) { throw "Upload failed." }
} finally { Remove-Item Env:\TWINE_PASSWORD -ErrorAction SilentlyContinue }
