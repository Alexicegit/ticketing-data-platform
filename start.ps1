# Move to project root
Set-Location $PSScriptRoot

# Activate virtual environment
. .\venv\Scripts\Activate.ps1

# Load environment variables
. .\load_env.ps1

Write-Host "Environment ready"
Write-Host "Python: $(python --version)"