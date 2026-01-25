# Vercel PR #14646 Implementation Guide

## Overview

This document describes the implementation of Vercel PR #14646, which introduces an **experimental Python runtime framework preset** for improved support of Python frameworks like FastAPI, Flask, and Starlette on Vercel.

## What Changed

### 1. Updated `vercel.json` Configuration

**Key Updates:**
- **Explicit Runtime Version**: Specified `@vercel/python@6.2.1` to use the latest Python runtime with experimental framework support
- **Python Version**: Explicitly set `runtime: "python3.12"` to align with Vercel's default Python version
- **Bundle Optimization**: Added comprehensive `excludeFiles` configuration to reduce serverless bundle size
- **Function Configuration**: Added `memory` and `maxDuration` settings in the build config (Vercel requires these in `config` section, not separate `functions` section)

**New Configuration Features:**
```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python@6.2.1",
      "config": {
        "maxLambdaSize": "50mb",
        "runtime": "python3.12",
        "memory": 3008,
        "maxDuration": 60,
        "excludeFiles": "{tests/**,test_*.py,*_test.py,docs/**,*.md,tmp/**,*.log,*.db,*.db-journal,dossiers/**,ios/**,windows/**,flutter/**,cli/**,.streamlit/secrets.toml,chatbot_history.db,.cache/**,__pycache__/**,*.pyc}"
      }
    }
  ]
}
```

### 2. Enhanced API Handler

**File**: `api/index.py`

Updated the handler to better leverage Vercel's experimental framework preset:
- Added comprehensive docstrings explaining the integration
- Exported both `app` and `handler` for better framework detection
- Added `__all__` for explicit module exports

### 3. Bundle Size Optimization

The `excludeFiles` configuration excludes:
- Test files and directories (`tests/**`, `test_*.py`, `*_test.py`)
- Documentation files (`docs/**`, `*.md`)
- Platform-specific directories (`ios/**`, `windows/**`, `flutter/**`)
- Development artifacts (`tmp/**`, `*.log`, `*.pyc`, `__pycache__/**`)
- Database files (`*.db`, `*.db-journal`, `dossiers/**`)
- Streamlit secrets (`.streamlit/secrets.toml`)

This keeps the serverless bundle under the 250MB limit recommended by Vercel.

## Benefits of PR #14646

1. **Automatic Framework Detection**: Vercel automatically detects and optimizes ASGI applications like FastAPI
2. **Improved Performance**: Better cold start times and runtime performance
3. **Simplified Configuration**: Less boilerplate needed for Python framework deployments
4. **Better Bundle Management**: Explicit control over what gets included in serverless functions
5. **Python 3.12 Support**: Uses the latest stable Python version (3.12) by default
6. **Streaming Response Support**: Enhanced support for streaming responses in Python frameworks

## Compatibility

- **Python Version**: 3.12 (as specified in `.python-version` and `pyproject.toml`)
- **FastAPI Version**: >=0.104.0 (compatible with the new runtime)
- **Vercel Python Runtime**: @vercel/python@6.2.1

## Testing the Implementation

To verify the implementation:

1. **Local Testing**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the FastAPI application locally
   uvicorn backend.api.main:app --reload
   ```

2. **Vercel Deployment**:
   ```bash
   # Deploy to Vercel preview
   vercel
   
   # Deploy to production
   vercel --prod
   ```

3. **Verify Endpoints**:
   - Root: `https://your-app.vercel.app/`
   - Health Check: `https://your-app.vercel.app/health`
   - API Docs: `https://your-app.vercel.app/docs`
   - Authentication: `https://your-app.vercel.app/api/auth/*`

## Troubleshooting

### Bundle Size Issues
If deployment fails due to bundle size:
1. Review the `excludeFiles` configuration
2. Add more patterns to exclude unnecessary files
3. Consider using a lighter version of large dependencies

### Runtime Errors
If you encounter runtime errors:
1. Verify Python version matches (3.12)
2. Check that all dependencies are listed in `requirements.txt` or `pyproject.toml`
3. Review Vercel deployment logs for detailed error messages

### Framework Detection Issues
If Vercel doesn't detect the framework correctly:
1. Ensure `app` is exported in `api/index.py`
2. Verify the file structure matches Vercel's expectations
3. Check that FastAPI is properly initialized in `backend/api/main.py`

## Additional Resources

- [Vercel Python Runtime Documentation](https://vercel.com/docs/functions/runtimes/python)
- [Vercel PR #14646](https://github.com/vercel/vercel/pull/14646)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/vercel/)
- [Python 3.12 Release Notes](https://docs.python.org/3.12/whatsnew/3.12.html)

## Migration Notes

This implementation is **backward compatible**. The changes enhance the existing deployment without breaking current functionality. All existing environment variables, routes, and authentication configurations remain unchanged.

### No Action Required For:
- Existing environment variables (API keys, auth settings)
- Authentication providers (Google, Microsoft, Apple)
- Database connections and configurations
- CORS settings
- API routes and endpoints

## Future Enhancements

The experimental framework preset may receive additional updates from Vercel. Stay tuned for:
- Enhanced streaming support
- Better cold start optimization
- Additional framework-specific presets
- Improved build caching
- Native Python SDK integrations (Vercel Blob, KV, etc.)
