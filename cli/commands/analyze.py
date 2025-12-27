"""Analysis commands."""

import os
from pathlib import Path

import click
import httpx
from rich.console import Console
from rich.panel import Panel

console = Console()
API_URL = os.getenv("THERAPY_REX_API_URL", "http://localhost:8000")


@click.command()
@click.option("--voice", type=click.Path(exists=True), help="Voice file path")
@click.option("--image", type=click.Path(exists=True), help="Image file path")
@click.option("--video", type=click.Path(exists=True), help="Video file path")
@click.option("--hand", help="Hand history text")
@click.option("--user-id", default="default", help="User ID")
def analyze(
    voice: str | None,
    image: str | None,
    video: str | None,
    hand: str | None,
    user_id: str,
) -> None:
    """Analyze voice, image, video, or hand history."""
    if voice:
        _analyze_voice(voice, user_id)
    elif image:
        _analyze_image(image, user_id)
    elif video:
        _analyze_video(video, user_id)
    elif hand:
        _analyze_hand(hand, user_id)
    else:
        console.print(
            "[red]Error: Specify --voice, --image, --video, or --hand[/red]"
        )


def _analyze_voice(file_path: str, user_id: str) -> None:
    """Analyze voice recording."""
    console.print(
        Panel.fit(
            "[bold cyan]Voice Analysis[/bold cyan]",
            border_style="cyan",
        )
    )
    
    with console.status("[bold green]Transcribing audio...", spinner="dots"):
        try:
            with open(file_path, "rb") as f:
                files = {"audio": (Path(file_path).name, f, "audio/wav")}
                response = httpx.post(
                    f"{API_URL}/api/analyze/voice",
                    files=files,
                    data={"user_id": user_id},
                    timeout=60.0,
                )
                response.raise_for_status()
                result = response.json()
                
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            return
    
    # Display results
    console.print(
        Panel(
            result["transcript"],
            title="[cyan]Transcript[/cyan]",
            border_style="cyan",
        )
    )
    
    console.print(
        Panel(
            result["therapeutic_response"],
            title="[cyan]Therapeutic Response[/cyan]",
            border_style="cyan",
        )
    )
    
    console.print(f"\n[dim]Models used: {', '.join(result['models'])}[/dim]")


def _analyze_image(file_path: str, user_id: str) -> None:
    """Analyze HUD screenshot."""
    console.print("[yellow]Image analysis not yet implemented[/yellow]")


def _analyze_video(file_path: str, user_id: str) -> None:
    """Analyze session video."""
    console.print("[yellow]Video analysis not yet implemented[/yellow]")


def _analyze_hand(hand_history: str, user_id: str) -> None:
    """Analyze poker hand."""
    console.print(
        Panel.fit(
            "[bold cyan]Hand Analysis[/bold cyan]",
            border_style="cyan",
        )
    )
    
    with console.status("[bold green]Analyzing hand...", spinner="dots"):
        try:
            response = httpx.post(
                f"{API_URL}/api/analyze/hand",
                json={
                    "hand_history": hand_history,
                    "emotional_context": "",
                    "user_id": user_id,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()
            
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            return
    
    # Display results
    console.print(
        Panel(
            result["gto_analysis"],
            title="[cyan]GTO Analysis[/cyan]",
            border_style="cyan",
        )
    )
    
    console.print(
        Panel(
            result["meta_context"],
            title="[cyan]Meta Context[/cyan]",
            border_style="cyan",
        )
    )
    
    if result.get("learning_points"):
        console.print("\n[bold cyan]Learning Points:[/bold cyan]")
        for point in result["learning_points"]:
            console.print(f"  • {point}")
    
    console.print(f"\n[dim]Models used: {', '.join(result['models'])}[/dim]")
