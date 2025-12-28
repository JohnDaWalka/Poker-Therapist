"""Deep therapy session command."""

import os

import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt

console = Console()
API_URL = os.getenv("THERAPY_REX_API_URL", "http://localhost:8000")


@click.command()
@click.option("--user-id", default="default", help="User ID")
def deep(user_id: str) -> None:
    """Deep therapy session (45-90 min)."""
    console.print(
        Panel.fit(
            "[bold magenta]Therapy Rex - Deep Session[/bold magenta]\n"
            "Structured 45-90 minute therapy",
            border_style="magenta",
        )
    )
    
    # Gather emotional state
    console.print("\n[yellow]Rate your current state (1-10):[/yellow]")
    stress = IntPrompt.ask("  Stress level", default=5)
    confidence = IntPrompt.ask("  Confidence level", default=5)
    motivation = IntPrompt.ask("  Motivation level", default=5)
    
    # Gather context
    recent_results = Prompt.ask(
        "\n[yellow]Recent poker results and situations?[/yellow]"
    )
    
    life_context = Prompt.ask(
        "\n[yellow]Life context affecting your game? (optional)[/yellow]",
        default="",
    )
    
    recurring_themes = Prompt.ask(
        "\n[yellow]Recurring issues or patterns? (optional)[/yellow]",
        default="",
    )
    
    # Show loading
    with console.status(
        "[bold magenta]Conducting therapy session...", spinner="dots"
    ):
        try:
            # Call API
            response = httpx.post(
                f"{API_URL}/api/deep-session",
                json={
                    "emotional_state": {
                        "stress": stress,
                        "confidence": confidence,
                        "motivation": motivation,
                    },
                    "recent_results": recent_results,
                    "life_context": life_context,
                    "recurring_themes": recurring_themes,
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
    console.print("\n")
    console.print(
        Panel(
            result["session_summary"],
            title="[magenta]Session Summary[/magenta]",
            border_style="magenta",
        )
    )
    
    # Show cognitive reframes
    if result.get("cognitive_reframes"):
        console.print("\n[bold magenta]Cognitive Reframes:[/bold magenta]")
        for reframe in result["cognitive_reframes"]:
            console.print(f"  • {reframe}")
    
    # Show action plan
    if result.get("action_plan"):
        console.print("\n[bold magenta]Action Plan:[/bold magenta]")
        for item in result["action_plan"]:
            console.print(
                f"  [{item['category']}] {item['action']} - {item['timeline']}"
            )
    
    # Show follow-up themes
    if result.get("follow_up_themes"):
        console.print("\n[bold magenta]Follow-up Themes:[/bold magenta]")
        for theme in result["follow_up_themes"]:
            console.print(f"  • {theme}")
    
    console.print("\n[green]✓ Deep session complete[/green]")
