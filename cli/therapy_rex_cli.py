"""Therapy Rex CLI main entry point."""

import os
import sys

import click
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import commands
from cli.commands import analyze, deep, profile, triage

# API URL configuration
API_URL = os.getenv("THERAPY_REX_API_URL", "http://localhost:8000")


@click.group()
@click.version_option(version="1.0.0")
def cli() -> None:
    """Therapy Rex - Poker Mental Game Coaching CLI."""
    pass


# Register commands
cli.add_command(triage.triage)
cli.add_command(deep.deep)
cli.add_command(analyze.analyze)
cli.add_command(profile.profile)
cli.add_command(profile.stats)
cli.add_command(profile.playbook)


if __name__ == "__main__":
    cli()
