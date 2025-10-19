# PowerShell setup script for Flask Image Blender

Write-Host "Setting up Flask Image Blender on Windows..." -ForegroundColor Green

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Create virtual environment
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create directories
$directories = @("static\uploads", "static\css", "static\js")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir
    }
}

Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "Run 'python some_app.py' to start the application" -ForegroundColor Cyan
