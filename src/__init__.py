"""
Shark - Cross-platform repository with full Windows compatibility

This package provides utilities and tools for cross-platform development
with special emphasis on Windows compatibility.
"""

__version__ = "0.1.0"
__author__ = "JohnDaWalka"

from .platform_utils import PlatformInfo, PathUtils, WindowsUtils, print_platform_info

__all__ = [
    "PlatformInfo",
    "PathUtils",
    "WindowsUtils",
    "print_platform_info",
]
