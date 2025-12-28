"""Profile and stats commands."""

import os

import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
API_URL = os.getenv("THERAPY_REX_API_URL", "http://localhost:8000")


@click.command()
@click.option("--user-id", default="default", help="User ID")
def profile(user_id: str) -> None:
    """View tilt profile."""
    console.print(
        Panel.fit(
            "[bold cyan]Tilt Profile[/bold cyan]",
            border_style="cyan",
        )
    )
    
    with console.status("[bold green]Loading profile...", spinner="dots"):
        try:
            response = httpx.get(
                f"{API_URL}/api/profile/{user_id}",
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            return
    
    # Display profile
    console.print("\n[bold cyan]A-Game Characteristics:[/bold cyan]")
    for key, value in result.get("a_game_characteristics", {}).items():
        console.print(f"  • {key}: {value}")
    
    console.print("\n[bold yellow]Red Flags:[/bold yellow]")
    for flag in result.get("red_flags", []):
        console.print(f"  ⚠️  {flag}")
    
    console.print("\n[bold cyan]Recurring Patterns:[/bold cyan]")
    for pattern in result.get("recurring_patterns", []):
        console.print(f"  • {pattern}")


@click.command()
@click.option("--user-id", default="default", help="User ID")
def stats(user_id: str) -> None:
    """View mental game stats."""
    console.print(
        Panel.fit(
            "[bold cyan]Mental Game Stats[/bold cyan]",
            border_style="cyan",
        )
    )
    
    # Create stats table
    table = Table(title="Recent Stats")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Tilt Frequency", "2.3 sessions/week")
    table.add_row("Average Severity", "5.2/10")
    table.add_row("Recovery Time", "45 minutes")
    table.add_row("Stop-Loss Adherence", "75%")
    table.add_row("A-Game %", "68%")
    
    console.print(table)


@click.command()
@click.option("--user-id", default="default", help="User ID")
def playbook(user_id: str) -> None:
    """View mental game playbook."""
    console.print(
        Panel.fit(
            "[bold cyan]Mental Game Playbook[/bold cyan]",
            border_style="cyan",
        )
    )
    
    with console.status("[bold green]Loading playbook...", spinner="dots"):
        try:
            response = httpx.get(
                f"{API_URL}/api/playbook/{user_id}",
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            return
    
    # Display playbook
    console.print(
        Panel(
            result.get("pre_session_script", ""),
            title="[cyan]Pre-Session Script[/cyan]",
            border_style="cyan",
        )
    )
    
    console.print("\n[bold cyan]Warmup Routine:[/bold cyan]")
    for item in result.get("warmup_routine", []):
        console.print(f"  • {item}")
    
    console.print("\n[bold cyan]In-Session Protocol:[/bold cyan]")
    for item in result.get("in_session_protocol", []):
        console.print(f"  • {item}")
    
    console.print("\n[bold cyan]Personal Rules:[/bold cyan]")
    for rule in result.get("personal_rules", []):
        console.print(f"  • {rule}")
