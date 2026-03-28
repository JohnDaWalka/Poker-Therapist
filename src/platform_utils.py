"""
Platform Detection and Compatibility Utilities for Shark

This module provides cross-platform utilities with special handling for Windows.
"""

import os
import platform
import sys
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any


class PlatformInfo:
    """Provides information about the current platform."""

    def __init__(self):
        self.system = platform.system()
        self.release = platform.release()
        self.version = platform.version()
        self.machine = platform.machine()
        self.processor = platform.processor()
        self.python_version = platform.python_version()

    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return self.system == "Windows"

    def is_linux(self) -> bool:
        """Check if running on Linux."""
        return self.system == "Linux"

    def is_macos(self) -> bool:
        """Check if running on macOS."""
        return self.system == "Darwin"

    def get_windows_version(self) -> Optional[str]:
        """Get Windows version information."""
        if not self.is_windows():
            return None

        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            )
            product_name = winreg.QueryValueEx(key, "ProductName")[0]
            build = winreg.QueryValueEx(key, "CurrentBuild")[0]
            winreg.CloseKey(key)
            return f"{product_name} (Build {build})"
        except Exception:
            return f"Windows {self.release}"

    def supports_long_paths(self) -> bool:
        """Check if Windows long path support is enabled."""
        if not self.is_windows():
            return True  # Non-Windows systems don't have this limitation

        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\FileSystem"
            )
            value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
            winreg.CloseKey(key)
            return value == 1
        except Exception:
            return False

    def get_info_dict(self) -> Dict[str, Any]:
        """Get all platform information as a dictionary."""
        info = {
            "system": self.system,
            "release": self.release,
            "version": self.version,
            "machine": self.machine,
            "processor": self.processor,
            "python_version": self.python_version,
            "is_windows": self.is_windows(),
            "is_linux": self.is_linux(),
            "is_macos": self.is_macos(),
        }

        if self.is_windows():
            info["windows_version"] = self.get_windows_version()
            info["long_paths_enabled"] = self.supports_long_paths()

        return info

    def __str__(self) -> str:
        """String representation of platform information."""
        return (
            f"Platform: {self.system} {self.release}\n"
            f"Machine: {self.machine}\n"
            f"Python: {self.python_version}"
        )


class PathUtils:
    """Cross-platform path utilities."""

    @staticmethod
    def normalize_path(path: str) -> Path:
        """
        Normalize a path for the current platform.

        Args:
            path: Input path string

        Returns:
            Normalized Path object
        """
        return Path(path).resolve()

    @staticmethod
    def to_posix_path(path: str) -> str:
        """
        Convert path to POSIX format (forward slashes).

        Args:
            path: Input path string

        Returns:
            Path with forward slashes
        """
        return Path(path).as_posix()

    @staticmethod
    def ensure_dir(path: str) -> Path:
        """
        Ensure directory exists, creating it if necessary.

        Args:
            path: Directory path

        Returns:
            Path object to the directory
        """
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    @staticmethod
    def get_home_dir() -> Path:
        """Get user home directory in a cross-platform way."""
        return Path.home()

    @staticmethod
    def get_temp_dir() -> Path:
        """Get temporary directory in a cross-platform way."""
        return Path(tempfile.gettempdir())


class WindowsUtils:
    """Windows-specific utilities."""

    @staticmethod
    def is_admin() -> bool:
        """Check if running with administrator privileges on Windows."""
        if platform.system() != "Windows":
            return False

        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    @staticmethod
    def get_environment_variable(name: str, scope: str = "user") -> Optional[str]:
        """
        Get environment variable on Windows.

        Args:
            name: Variable name
            scope: 'user' or 'machine'

        Returns:
            Variable value or None
        """
        if platform.system() != "Windows":
            return os.environ.get(name)

        try:
            import winreg
            if scope == "user":
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Environment"
                )
            else:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                )
            value, _ = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return value
        except Exception:
            return None


def print_platform_info():
    """Print detailed platform information."""
    info = PlatformInfo()
    print("=" * 60)
    print("Shark Platform Information")
    print("=" * 60)
    print(info)
    print()

    if info.is_windows():
        print(f"Windows Version: {info.get_windows_version()}")
        print(f"Long Paths Enabled: {info.supports_long_paths()}")
        print(f"Running as Admin: {WindowsUtils.is_admin()}")
    print("=" * 60)


if __name__ == "__main__":
    # When run as a script, print platform information
    print_platform_info()
