# Contributing to Shark

Thank you for your interest in contributing to Shark! This document provides guidelines for contributing to this cross-platform project.

## 🌐 Cross-Platform Development

Shark is designed to work on all major platforms. When contributing, please ensure your changes work on:

- Windows 10/11 and Windows Server 2016+
- Linux distributions (Ubuntu, Debian, RHEL, etc.)
- macOS 10.15 and later

## 🔧 Development Setup

### For Windows Users

1. Install Git for Windows from [git-scm.com](https://git-scm.com/download/win)
2. Clone the repository:
   ```bash
   git clone https://github.com/JohnDaWalka/Shark.git
   cd Shark
   ```
3. Run the Windows setup script:
   ```powershell
   .\scripts\setup-windows.ps1
   ```
4. See [Windows Setup Guide](docs/WINDOWS_SETUP.md) for detailed instructions

### For Linux/macOS Users

1. Clone the repository:
   ```bash
   git clone https://github.com/JohnDaWalka/Shark.git
   cd Shark
   ```
2. Follow standard development practices for your platform

## 📝 Code Style

### General Guidelines

- Follow the EditorConfig settings (`.editorconfig`)
- Use consistent indentation (spaces, not tabs for most files)
- Keep line endings consistent (handled by `.gitattributes`)
- Write clear, self-documenting code
- Add comments only when necessary to explain complex logic

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Use meaningful variable and function names

### Platform-Specific Code

When writing platform-specific code:

```python
import platform

if platform.system() == "Windows":
    # Windows-specific code
    pass
elif platform.system() == "Linux":
    # Linux-specific code
    pass
elif platform.system() == "Darwin":
    # macOS-specific code
    pass
```

Or use the provided utilities:

```python
from src.platform_utils import PlatformInfo

platform_info = PlatformInfo()
if platform_info.is_windows():
    # Windows-specific code
    pass
```

## 🧪 Testing

### Running Tests

Before submitting a pull request, ensure all tests pass:

```bash
# Run tests (when test suite is implemented)
python -m pytest

# Or use platform-specific scripts
.\scripts\test-windows.ps1  # Windows PowerShell
scripts\test-windows.bat     # Windows Command Prompt
./scripts/test-linux.sh      # Linux/macOS
```

### Writing Tests

- Write tests for all new features
- Ensure tests work on all supported platforms
- Use platform detection when necessary for platform-specific tests
- Test edge cases and error conditions

## 🚀 Pull Request Process

1. **Fork the repository** and create a new branch from `main`
2. **Make your changes** following the guidelines above
3. **Test your changes** on multiple platforms when possible
4. **Update documentation** if you're changing functionality
5. **Run the CI checks** by pushing to your fork
6. **Submit a pull request** with a clear description of changes

### Pull Request Checklist

- [ ] Code follows the project's style guidelines
- [ ] Changes work on Windows, Linux, and macOS (or note any platform limitations)
- [ ] Documentation has been updated (if needed)
- [ ] All tests pass
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary files are included (build artifacts, IDE files, etc.)

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Platform information**: OS name, version, and architecture
2. **Steps to reproduce**: Clear steps to reproduce the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Logs/Screenshots**: Any relevant error messages or screenshots

For Windows-specific issues, also include:
- Windows version (run `winver` or `systeminfo`)
- PowerShell version (run `$PSVersionTable.PSVersion`)
- Whether long path support is enabled

## 💡 Feature Requests

Feature requests are welcome! Please:

1. Check if the feature has already been requested
2. Clearly describe the feature and its use case
3. Explain how it benefits the project
4. Consider cross-platform implications

## 🔐 Security

If you discover a security vulnerability, please **do not** open a public issue. Instead:

1. Email the details to the repository maintainers
2. Provide steps to reproduce the vulnerability
3. Allow time for a fix before public disclosure

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race
- Ethnicity
- Age
- Religion
- Nationality

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Personal or political attacks
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

## 📚 Resources

- [Windows Setup Guide](docs/WINDOWS_SETUP.md)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Writing Good Commit Messages](https://chris.beams.io/posts/git-commit/)
- [EditorConfig](https://editorconfig.org/)

## ❓ Questions?

If you have questions about contributing:
1. Check the documentation first
2. Search existing issues and discussions
3. Open a new discussion or issue if your question hasn't been answered

Thank you for contributing to Shark! 🦈
