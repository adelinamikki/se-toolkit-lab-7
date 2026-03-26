from typing import Optional

from config import BotConfig
from services.lms_client import LMSClient


def handle_start() -> str:
    """Welcome message."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    """List all available commands."""
    return (
        "Available commands:\n"
        "/start — welcome message\n"
        "/help — show this message\n"
        "/health — check backend status\n"
        "/labs — list available labs\n"
        "/scores <lab-id> — show per-task scores (e.g., /scores lab-04)"
    )


def handle_health() -> str:
    """Check backend health and report item count."""
    config = BotConfig()
    client = LMSClient(config)

    items = client.get_items()
    if items is None:
        return client.get_last_error()

    count = len(items)
    return f"Backend is healthy. {count} items available."


def handle_labs() -> str:
    """List available labs."""
    config = BotConfig()
    client = LMSClient(config)

    items = client.get_items()
    if items is None:
        return client.get_last_error()

    labs = [item for item in items if item.get("type") == "lab"]

    if not labs:
        return "No labs found in the backend."

    lines = ["Available labs:"]
    for lab in labs:
        title = lab.get("title", "Unknown")
        lines.append(f"- {title}")

    return "\n".join(lines)


def handle_scores(argument: Optional[str] = None) -> str:
    """Show per-task pass rates for a lab."""
    if not argument:
        return "Usage: /scores <lab-id>\nExample: /scores lab-04"

    config = BotConfig()
    client = LMSClient(config)

    pass_rates = client.get_pass_rates(argument)
    if pass_rates is None:
        return client.get_last_error()

    if not pass_rates:
        return f"No data found for lab {argument}."

    lines = [f"Pass rates for {argument}:"]
    for task_name, rate_info in pass_rates.items():
        if isinstance(rate_info, dict):
            rate = rate_info.get("pass_rate", 0)
            attempts = rate_info.get("attempts", 0)
            lines.append(f"- {task_name}: {rate:.1f}% ({attempts} attempts)")
        else:
            lines.append(f"- {task_name}: {rate_info}")

    return "\n".join(lines)


def handle_unknown(command: str) -> str:
    """Handle unknown commands."""
    return f"Unknown command: {command}. Type /help for the command list."