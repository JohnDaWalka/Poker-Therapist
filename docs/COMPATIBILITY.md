# Shark Repository

## Cross-Platform Compatibility Matrix

This document tracks the compatibility of Shark across different operating systems and environments.

## Operating Systems

| OS | Version | Status | Notes |
|---|---|---|---|
| Windows 11 | All editions | ✅ Supported | Full compatibility |
| Windows 10 | 1809+ | ✅ Supported | Requires version 1809 or later |
| Windows Server 2022 | - | ✅ Supported | Tested in CI |
| Windows Server 2019 | - | ✅ Supported | Tested in CI |
| Windows Server 2016 | - | ✅ Supported | Compatible |
| Ubuntu | 20.04+ | ✅ Supported | Primary Linux target |
| Debian | 10+ | ✅ Supported | Compatible |
| RHEL/CentOS | 8+ | ✅ Supported | Compatible |
| macOS | 10.15+ | ✅ Supported | Catalina and later |

## Python Support

| Python Version | Windows | Linux | macOS |
|---|---|---|---|
| 3.8 | ✅ | ✅ | ✅ |
| 3.9 | ✅ | ✅ | ✅ |
| 3.10 | ✅ | ✅ | ✅ |
| 3.11 | ✅ | ✅ | ✅ |
| 3.12 | ✅ | ✅ | ✅ |

## Features

| Feature | Windows | Linux | macOS | Notes |
|---|---|---|---|---|
| Platform Detection | ✅ | ✅ | ✅ | Full support |
| Path Utilities | ✅ | ✅ | ✅ | Cross-platform |
| Long Path Support | ✅ | N/A | N/A | Windows-specific |
| Admin Detection | ✅ | ❌ | ❌ | Windows only |
| Line Endings | ✅ | ✅ | ✅ | Auto-managed via .gitattributes |

## CI/CD

| CI Platform | Windows | Linux | macOS | Status |
|---|---|---|---|---|
| GitHub Actions | ✅ | ✅ | ✅ | Active |

## Known Limitations

### Windows

1. **Long Path Support**: Requires Windows 10 1607+ and registry modification
2. **Case Sensitivity**: Windows filesystem is case-insensitive by default
3. **Path Length**: 260 character limit unless long paths are enabled
4. **Line Endings**: CRLF is default, but handled automatically by Git

### Linux

- None currently identified

### macOS

- None currently identified

## Testing

All features are tested across platforms in CI:
- Unit tests run on Windows, Linux, and macOS
- Integration tests verify cross-platform compatibility
- Manual testing performed on various Windows versions

## Future Compatibility

Planned support for:
- Additional Linux distributions
- Older Windows versions (on request)
- ARM architecture (Windows on ARM, Apple Silicon)

## Reporting Issues

When reporting compatibility issues, please include:
- Operating system and version
- Python version
- Error messages or logs
- Steps to reproduce

Label issues with platform-specific tags:
- `windows` for Windows-specific issues
- `linux` for Linux-specific issues
- `macos` for macOS-specific issues
- `cross-platform` for issues affecting multiple platforms
