"""Guided breathing exercise UI."""

import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

console = Console()


def show_breathing_exercise(exercise_name: str = "4-7-8 breathing") -> None:
    """Show guided breathing exercise.
    
    Args:
        exercise_name: Name of breathing exercise
    """
    console.print(
        Panel(
            f"[bold cyan]{exercise_name}[/bold cyan]\n"
            "Follow the guided breathing exercise",
            border_style="cyan",
        )
    )
    
    if "4-7-8" in exercise_name.lower():
        _do_478_breathing()
    elif "box" in exercise_name.lower() or "4-4-4-4" in exercise_name:
        _do_box_breathing()
    elif "5-5" in exercise_name:
        _do_55_breathing()
    else:
        _do_478_breathing()  # Default
    
    console.print("\n[green]✓ Breathing exercise complete[/green]")


def _do_478_breathing(cycles: int = 4) -> None:
    """4-7-8 breathing pattern.
    
    Args:
        cycles: Number of cycles
    """
    for cycle in range(1, cycles + 1):
        console.print(f"\n[cyan]Cycle {cycle}/{cycles}[/cyan]")
        
        # Breathe in (4 seconds)
        console.print("[yellow]Breathe IN...[/yellow]", end="")
        _countdown(4)
        
        # Hold (7 seconds)
        console.print("[blue]HOLD...[/blue]", end="")
        _countdown(7)
        
        # Breathe out (8 seconds)
        console.print("[green]Breathe OUT...[/green]", end="")
        _countdown(8)


def _do_box_breathing(cycles: int = 4) -> None:
    """Box breathing pattern (4-4-4-4).
    
    Args:
        cycles: Number of cycles
    """
    for cycle in range(1, cycles + 1):
        console.print(f"\n[cyan]Cycle {cycle}/{cycles}[/cyan]")
        
        console.print("[yellow]Breathe IN...[/yellow]", end="")
        _countdown(4)
        
        console.print("[blue]HOLD...[/blue]", end="")
        _countdown(4)
        
        console.print("[green]Breathe OUT...[/green]", end="")
        _countdown(4)
        
        console.print("[blue]HOLD...[/blue]", end="")
        _countdown(4)


def _do_55_breathing(cycles: int = 5) -> None:
    """5-5 breathing pattern.
    
    Args:
        cycles: Number of cycles
    """
    for cycle in range(1, cycles + 1):
        console.print(f"\n[cyan]Cycle {cycle}/{cycles}[/cyan]")
        
        console.print("[yellow]Breathe IN...[/yellow]", end="")
        _countdown(5)
        
        console.print("[green]Breathe OUT...[/green]", end="")
        _countdown(5)


def _countdown(seconds: int) -> None:
    """Show countdown timer.
    
    Args:
        seconds: Number of seconds
    """
    for i in range(seconds, 0, -1):
        console.print(f" {i}", end="", style="bold")
        time.sleep(1)
    console.print()
