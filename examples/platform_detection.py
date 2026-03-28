"""
Example: Platform Detection and Cross-Platform Code

This example demonstrates how to use Shark's platform utilities
to write code that adapts to different operating systems.
"""

import sys
from pathlib import Path

# Add parent directory to path for examples
# Note: In production code, install the package properly instead
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.platform_utils import PlatformInfo, PathUtils, WindowsUtils


def main():
    """Main example function demonstrating cross-platform utilities."""

    print("=" * 70)
    print("Shark Platform Detection Example")
    print("=" * 70)
    print()

    # Create platform info object
    platform = PlatformInfo()

    # Basic platform detection
    print("1. Basic Platform Detection:")
    print(f"   Operating System: {platform.system}")
    print(f"   Release: {platform.release}")
    print(f"   Machine: {platform.machine}")
    print(f"   Python Version: {platform.python_version}")
    print()

    # Platform-specific checks
    print("2. Platform-Specific Checks:")
    print(f"   Is Windows: {platform.is_windows()}")
    print(f"   Is Linux: {platform.is_linux()}")
    print(f"   Is macOS: {platform.is_macos()}")
    print()

    # Windows-specific information
    if platform.is_windows():
        print("3. Windows-Specific Information:")
        print(f"   Windows Version: {platform.get_windows_version()}")
        print(f"   Long Paths Enabled: {platform.supports_long_paths()}")
        print(f"   Running as Admin: {WindowsUtils.is_admin()}")
        print()

        if not platform.supports_long_paths():
            print("   ⚠️  Warning: Long path support is not enabled.")
            print("   Some file operations may fail with long paths.")
            print()

    # Path handling examples
    print("4. Cross-Platform Path Handling:")
    home_dir = PathUtils.get_home_dir()
    temp_dir = PathUtils.get_temp_dir()
    print(f"   Home Directory: {home_dir}")
    print(f"   Temp Directory: {temp_dir}")
    print(f"   Home (POSIX): {PathUtils.to_posix_path(str(home_dir))}")
    print()

    # Platform-specific behavior
    print("5. Platform-Specific Behavior Example:")
    if platform.is_windows():
        print("   Executing Windows-specific code...")
        print("   - Using Windows registry for configuration")
        print("   - Handling CRLF line endings")
        print("   - Checking for long path support")
    elif platform.is_linux():
        print("   Executing Linux-specific code...")
        print("   - Using /etc for configuration")
        print("   - Handling LF line endings")
        print("   - No path length limitations")
    elif platform.is_macos():
        print("   Executing macOS-specific code...")
        print("   - Using ~/Library for configuration")
        print("   - Handling LF line endings")
        print("   - No path length limitations")
    print()

    # Full information dictionary
    print("6. Complete Platform Information:")
    info_dict = platform.get_info_dict()
    for key, value in info_dict.items():
        print(f"   {key}: {value}")
    print()

    print("=" * 70)
    print("Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
