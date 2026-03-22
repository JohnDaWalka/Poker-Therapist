"""Vercel serverless entrypoint for the Poker-Coach-Grind FastAPI application.

Vercel invokes this file as a Python serverless function.  The project layout
uses relative imports throughout (``from ..database.session import ...``), so
we must reconstruct the package hierarchy in ``sys.modules`` before importing
``api.main``.  We also redirect the SQLite database path to ``/tmp/`` which is
the only writable location in Vercel's sandbox.
"""

import os
import sys
import types
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Point the database at /tmp so writes succeed in the serverless sandbox.
# ---------------------------------------------------------------------------
os.environ.setdefault(
    "GRIND_DATABASE_URL",
    "sqlite+aiosqlite:////tmp/poker_grind.db",
)

# ---------------------------------------------------------------------------
# 2. Ensure the project root (poker-coach-grind/) is on sys.path so that
#    absolute module lookups work alongside the synthetic package below.
# ---------------------------------------------------------------------------
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# ---------------------------------------------------------------------------
# 3. Register synthetic package modules so that relative imports inside
#    api/main.py (e.g. ``from ..database.session import init_database``)
#    resolve correctly.  Without this, Python has no parent package for the
#    ``api`` sub-package because Vercel executes api/index.py directly.
# ---------------------------------------------------------------------------
_PKG = "poker_coach_grind"


def _register_package(name: str, path: str) -> types.ModuleType:
    """Create and register a synthetic package in sys.modules."""
    mod = types.ModuleType(name)
    mod.__path__ = [path]  # type: ignore[attr-defined]
    mod.__package__ = name
    sys.modules[name] = mod
    return mod


_root_pkg = _register_package(_PKG, _project_root)

for _sub in ("api", "database", "models", "crypto", "cli"):
    _sub_mod = _register_package(
        f"{_PKG}.{_sub}",
        str(Path(_project_root) / _sub),
    )
    setattr(_root_pkg, _sub, _sub_mod)

# ---------------------------------------------------------------------------
# 4. Import the FastAPI application.  All relative imports inside the project
#    will now resolve through the synthetic package tree created above.
# ---------------------------------------------------------------------------
from poker_coach_grind.api.main import app  # noqa: E402

# ---------------------------------------------------------------------------
# 5. Export as ``handler`` – the symbol Vercel's Python runtime expects.
# ---------------------------------------------------------------------------
handler = app
