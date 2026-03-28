# Shark Windows Setup Script
# This script sets up the development environment on Windows

param(
    [switch]$SkipChecks,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Banner
Write-Host @"
╔═══════════════════════════════════════════════════════════╗
║           Shark Windows Setup Script                     ║
║           Setting up development environment...           ║
╚═══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check Windows version
Write-Host "`n[1/6] Checking Windows version..." -ForegroundColor Yellow
$os = Get-CimInstance Win32_OperatingSystem
Write-Host "  ✓ Windows version: $($os.Caption) (Build $($os.BuildNumber))" -ForegroundColor Green

# Check PowerShell version
Write-Host "`n[2/6] Checking PowerShell version..." -ForegroundColor Yellow
$psVersion = $PSVersionTable.PSVersion
Write-Host "  ✓ PowerShell version: $psVersion" -ForegroundColor Green

if ($psVersion.Major -lt 5) {
    Write-Host "  ⚠ Warning: PowerShell 5.0 or higher is recommended" -ForegroundColor Yellow
}

# Check Git installation
Write-Host "`n[3/6] Checking Git installation..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "  ✓ Git installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Git not found! Please install Git for Windows from https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

# Configure Git for Windows
Write-Host "`n[4/6] Configuring Git settings..." -ForegroundColor Yellow
git config --local core.autocrlf true
git config --local core.symlinks false
Write-Host "  ✓ Git configured for Windows" -ForegroundColor Green

# Check for long path support
Write-Host "`n[5/6] Checking long path support..." -ForegroundColor Yellow
$longPathsEnabled = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -ErrorAction SilentlyContinue

if ($longPathsEnabled.LongPathsEnabled -eq 1) {
    Write-Host "  ✓ Long path support is enabled" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Long path support is not enabled. Some file paths may fail." -ForegroundColor Yellow
    Write-Host "    Run this command as Administrator to enable:" -ForegroundColor Yellow
    Write-Host "    New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name 'LongPathsEnabled' -Value 1 -PropertyType DWORD -Force" -ForegroundColor Gray
}

# Display environment information
Write-Host "`n[6/6] Environment summary..." -ForegroundColor Yellow
Write-Host "  • Working directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host "  • User: $env:USERNAME" -ForegroundColor Cyan
Write-Host "  • Computer: $env:COMPUTERNAME" -ForegroundColor Cyan
Write-Host "  • Architecture: $env:PROCESSOR_ARCHITECTURE" -ForegroundColor Cyan

# Success message
Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✓ Windows environment setup complete!                   ║" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "║  Next steps:                                              ║" -ForegroundColor Green
Write-Host "║  1. Review docs/WINDOWS_SETUP.md for detailed info       ║" -ForegroundColor Green
Write-Host "║  2. Install required development tools                   ║" -ForegroundColor Green
Write-Host "║  3. Start developing!                                    ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
