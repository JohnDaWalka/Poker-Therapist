"""Triage command."""

import os

import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from cli.ui.breathing import show_breathing_exercise
from cli.ui.panels import create_severity_panel, create_warning_panel

console = Console()
API_URL = os.getenv("THERAPY_REX_API_URL", "http://localhost:8000")


@click.command()
@click.option("--user-id", default="default", help="User ID")
def triage(user_id: str) -> None:
    """Quick tilt intervention (5-10 min)."""
    console.print(
        Panel.fit(
            "[bold cyan]Therapy Rex - Quick Triage[/bold cyan]\n"
            "Emergency tilt intervention",
            border_style="cyan",
        )
    )
    
    # Gather input
    situation = Prompt.ask("\n[yellow]What's happening right now?[/yellow]")
    
    console.print("\n[yellow]What emotion are you feeling?[/yellow]")
    console.print("Options: Anger, Shame, Fear, Frustration, Entitlement, Boredom")
    emotion = Prompt.ask("Emotion", default="Frustration")
    
    intensity = IntPrompt.ask(
        "\n[yellow]Intensity level (1-10)[/yellow]",
        default=5,
    )
    
    body_sensation = Prompt.ask(
        "\n[yellow]Physical sensations (optional)[/yellow]",
        default="",
    )
    
    still_playing = Confirm.ask("\n[red]Are you still playing?[/red]", default=False)
    
    # Show loading
    with console.status("[bold green]Analyzing situation...", spinner="dots"):
        try:
            # Call API
            response = httpx.post(
                f"{API_URL}/api/triage",
                json={
                    "situation": situation,
                    "emotion": emotion,
                    "intensity": intensity,
                    "body_sensation": body_sensation,
                    "still_playing": still_playing,
                    "user_id": user_id,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            return
    
    # Display results
    console.print("\n")
    console.print(create_severity_panel(result["severity"]))
    
    # Show warning if needed
    if result.get("warning_message"):
        console.print(create_warning_panel(result["warning_message"]))
    
    # Show AI guidance
    if result.get("ai_guidance"):
        console.print(
            Panel(
                result["ai_guidance"],
                title="[cyan]Guidance[/cyan]",
                border_style="cyan",
            )
        )
    
    # Show micro plan
    if result.get("micro_plan"):
        console.print("\n[bold cyan]Action Plan:[/bold cyan]")
        for i, action in enumerate(result["micro_plan"], 1):
            console.print(f"  {i}. {action}")
    
    # Offer breathing exercise
    if Confirm.ask("\n[cyan]Practice breathing exercise?[/cyan]", default=True):
        show_breathing_exercise(result.get("breathing_exercise", "4-7-8 breathing"))
    
    console.print("\n[green]✓ Triage complete[/green]")
