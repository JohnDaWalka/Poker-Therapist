# Shark Examples

This directory contains example scripts demonstrating Shark's cross-platform capabilities.

## Running Examples

To run any example:

```bash
# On Windows (PowerShell)
python examples\platform_detection.py

# On Linux/macOS
python3 examples/platform_detection.py
```

## Available Examples

### platform_detection.py

Demonstrates how to:
- Detect the current operating system
- Get platform-specific information
- Use cross-platform path utilities
- Write code that adapts to different platforms
- Access Windows-specific features (when running on Windows)

**Output on Windows:**
```
1. Basic Platform Detection:
   Operating System: Windows
   Release: 10
   Machine: AMD64
   Python Version: 3.x.x

2. Platform-Specific Checks:
   Is Windows: True
   Is Linux: False
   Is macOS: False

3. Windows-Specific Information:
   Windows Version: Windows 10 Pro (Build 19045)
   Long Paths Enabled: True/False
   Running as Admin: True/False
```

**Output on Linux:**
```
1. Basic Platform Detection:
   Operating System: Linux
   Release: 5.x.x
   Machine: x86_64
   Python Version: 3.x.x

2. Platform-Specific Checks:
   Is Windows: False
   Is Linux: True
   Is macOS: False
```

**Output on macOS:**
```
1. Basic Platform Detection:
   Operating System: Darwin
   Release: 21.x.x
   Machine: x86_64
   Python Version: 3.x.x

2. Platform-Specific Checks:
   Is Windows: False
   Is Linux: False
   Is macOS: True
```

## Creating Your Own Examples

When creating examples that use Shark's utilities:

1. Import the necessary modules:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   
   from src.platform_utils import PlatformInfo, PathUtils, WindowsUtils
   ```

2. Use platform detection for conditional logic:
   ```python
   platform = PlatformInfo()
   if platform.is_windows():
       # Windows-specific code
       pass
   ```

3. Use PathUtils for cross-platform file operations:
   ```python
   home = PathUtils.get_home_dir()
   temp = PathUtils.get_temp_dir()
   normalized = PathUtils.normalize_path("/some/path")
   ```

4. Test your example on multiple platforms when possible

## Contributing Examples

If you have useful examples demonstrating Shark's capabilities:

1. Create a new Python file in this directory
2. Add clear documentation and comments
3. Test on multiple platforms
4. Update this README with your example
5. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for more details.
