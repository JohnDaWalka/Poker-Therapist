"""Utility helpers for running audit commands safely."""

from __future__ import annotations

import subprocess
from typing import Iterable, Sequence

# Limit which executables may be invoked by the audit pipeline.
ALLOWED_EXECUTABLES: set[str] = {"python", "pip", "npm"}


def run_command(executable: str, args: Sequence[str] | None = None) -> None:
    """Run an audit command without invoking a shell.

    Args:
        executable: The allowed executable to invoke.
        args: Optional additional arguments to pass as separate items.

    Raises:
        ValueError: If an unsupported executable is provided.
        subprocess.CalledProcessError: If the command exits with a non-zero status.
    """
    if executable not in ALLOWED_EXECUTABLES:
        raise ValueError(f"Unsupported executable: {executable}")

    command: list[str] = [executable]
    if args:
        command.extend(args)

    subprocess.run(command, check=True)


def run_pipeline(steps: Iterable[tuple[str, Sequence[str] | None]]) -> None:
    """Run a sequence of audit steps safely.

    Each step is a pair of (executable, args). The executable must be whitelisted
    in ALLOWED_EXECUTABLES and arguments are passed positionally to avoid shell
    injection.
    """
    for executable, args in steps:
        run_command(executable, args)
