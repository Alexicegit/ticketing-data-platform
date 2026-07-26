$envFile = Join-Path $PSScriptRoot ".env"

if (-not (Test-Path $envFile)) {
    throw ".env file not found: $envFile"
}

Get-Content $envFile | ForEach-Object {
    # Skip blank lines and comments
    if ($_ -match '^\s*$' -or $_ -match '^\s*#') {
        return
    }

    $name, $value = $_ -split '=', 2

    [Environment]::SetEnvironmentVariable(
        $name.Trim(),
        $value.Trim(),
        "Process"
    )
}

Write-Host "Environment variables loaded from $envFile"