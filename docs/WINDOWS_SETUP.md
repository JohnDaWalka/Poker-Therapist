# Windows Setup Guide

This guide provides instructions for setting up and using the Shark project on Windows operating systems.

## Supported Windows Versions

Shark is compatible with all modern Windows operating systems:

- ✅ Windows 11 (all editions)
- ✅ Windows 10 (version 1809 and later)
- ✅ Windows Server 2022
- ✅ Windows Server 2019
- ✅ Windows Server 2016

## Prerequisites

### Windows-Specific Requirements

1. **Windows Terminal** (Recommended)
   - Download from Microsoft Store or [GitHub](https://github.com/microsoft/terminal)
   - Provides better console experience than Command Prompt

2. **PowerShell 7+** (Recommended)
   - Download from [PowerShell GitHub Releases](https://github.com/PowerShell/PowerShell/releases)
   - Provides better cross-platform compatibility

3. **Git for Windows**
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Ensure "Git from the command line and 3rd-party software" is selected
   - Configure line endings: `git config --global core.autocrlf true`

### Development Tools

Choose your preferred development environment:

#### Option 1: WSL2 (Windows Subsystem for Linux) - Recommended
```powershell
# Enable WSL2
wsl --install

# Install Ubuntu (or your preferred distribution)
wsl --install -d Ubuntu

# Update WSL
wsl --update
```

#### Option 2: Native Windows Development
- Install your language runtime/SDK of choice
- Configure PATH environment variables
- Use Windows-native package managers (chocolatey, scoop, winget)

## Installation

### Using PowerShell

```powershell
# Clone the repository
git clone https://github.com/JohnDaWalka/Shark.git

# Navigate to the directory
cd Shark

# Verify git attributes are working
git config --local core.autocrlf true
```

### Using Windows Terminal

```bash
# Clone the repository
git clone https://github.com/JohnDaWalka/Shark.git

# Navigate to the directory
cd Shark
```

## Configuration

### Line Endings

The project uses `.gitattributes` to manage line endings automatically:
- Text files use LF (Unix-style) in the repository
- Windows-specific files (.bat, .cmd, .ps1) use CRLF
- Git automatically converts line endings on checkout/commit

### Environment Variables

Set environment variables using PowerShell:
```powershell
# Temporary (current session only)
$env:VARIABLE_NAME = "value"

# Permanent (user level)
[System.Environment]::SetEnvironmentVariable("VARIABLE_NAME", "value", "User")

# Permanent (system level, requires admin)
[System.Environment]::SetEnvironmentVariable("VARIABLE_NAME", "value", "Machine")
```

Or use Command Prompt:
```cmd
# Temporary
set VARIABLE_NAME=value

# Permanent (user level)
setx VARIABLE_NAME "value"
```

### Path Separators

The project handles path separators automatically:
- Use forward slashes `/` in code when possible (cross-platform)
- Use `os.path.join()` (Python) or `path.join()` (Node.js) for dynamic paths
- Windows automatically handles both `/` and `\` in most contexts

## Development Workflow

### PowerShell Scripts

Windows-specific automation scripts are provided:

```powershell
# Setup development environment
.\scripts\setup-windows.ps1

# Run tests
.\scripts\test-windows.ps1

# Build project
.\scripts\build-windows.ps1
```

### Batch Scripts

Alternative batch scripts for compatibility:

```cmd
# Setup development environment
scripts\setup-windows.bat

# Run tests
scripts\test-windows.bat

# Build project
scripts\build-windows.bat
```

## Troubleshooting

### Common Issues

#### 1. Line Ending Issues
**Problem**: Files have mixed line endings causing Git issues.

**Solution**:
```powershell
# Normalize line endings
git config core.autocrlf true
git rm --cached -r .
git reset --hard
```

#### 2. Path Length Limitations
**Problem**: Windows has a 260-character path length limit (MAX_PATH).

**Solution**:
```powershell
# Enable long path support (Windows 10 1607+)
# Run as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force

# Or enable via Group Policy:
# Computer Configuration > Administrative Templates > System > Filesystem > Enable Win32 long paths
```

#### 3. Permission Issues
**Problem**: Access denied errors when running scripts.

**Solution**:
```powershell
# Set execution policy (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine

# Or bypass for current session only
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

#### 4. Case Sensitivity
**Problem**: Windows filesystem is case-insensitive but Git is case-sensitive.

**Solution**:
```powershell
# Enable case sensitivity for specific directory (Windows 10 1803+)
fsutil.exe file setCaseSensitiveInfo C:\path\to\Shark enable
```

## Performance Optimization

### Windows Defender Exclusions

Add project directory to Windows Defender exclusions for better performance:

```powershell
# Run as Administrator
Add-MpPreference -ExclusionPath "C:\path\to\Shark"
```

### WSL2 Performance

For WSL2 users, store files in Linux filesystem for better performance:
```bash
# Store project in WSL filesystem, not /mnt/c/
cd ~
git clone https://github.com/JohnDaWalka/Shark.git
```

## CI/CD Integration

The project includes GitHub Actions workflows that test on multiple Windows versions:
- Windows Server 2022 (windows-2022)
- Windows Server 2019 (windows-2019)
- Windows Server latest (windows-latest)

See `.github/workflows/cross-platform.yml` for details.

## Additional Resources

- [Windows Terminal Documentation](https://docs.microsoft.com/en-us/windows/terminal/)
- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)
- [WSL2 Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Git for Windows Documentation](https://gitforwindows.org/)

## Support

For Windows-specific issues:
1. Check this guide first
2. Search existing GitHub issues
3. Create a new issue with the `windows` label
4. Include Windows version and PowerShell version in bug reports

## Contributing

When contributing Windows-specific code:
1. Test on multiple Windows versions
2. Use PowerShell 7+ for scripts
3. Follow EditorConfig settings
4. Ensure cross-platform compatibility when possible
