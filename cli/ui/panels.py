"""Rich panel components."""

from rich.panel import Panel


def create_severity_panel(severity: int) -> Panel:
    """Create severity indicator panel.
    
    Args:
        severity: Severity level 1-10
        
    Returns:
        Rich Panel
    """
    if severity >= 9:
        color = "bold red"
        emoji = "🚨"
        level = "CRITICAL"
    elif severity >= 7:
        color = "red"
        emoji = "🛑"
        level = "HIGH"
    elif severity >= 5:
        color = "yellow"
        emoji = "⚠️"
        level = "MODERATE"
    elif severity >= 3:
        color = "orange1"
        emoji = "⚡"
        level = "MILD"
    else:
        color = "green"
        emoji = "✓"
        level = "LOW"
    
    return Panel(
        f"[{color}]{emoji} Severity: {severity}/10 - {level}[/{color}]",
        border_style=color.replace("bold ", ""),
    )


def create_warning_panel(message: str) -> Panel:
    """Create warning panel.
    
    Args:
        message: Warning message
        
    Returns:
        Rich Panel
    """
    return Panel(
        f"[bold red]{message}[/bold red]",
        title="⚠️  WARNING",
        border_style="red",
    )
