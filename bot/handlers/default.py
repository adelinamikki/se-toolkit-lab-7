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

    labs = [
        item
        for item in items
        if item.get("type") == "lab"
        or str(item.get("title", "")).strip().lower().startswith("lab ")
    ]

    if not labs:
        return "No labs found in the backend."

    lines = ["Available labs:"]
    for lab in sorted(labs, key=lambda item: str(item.get("title", ""))):
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

    lab_label = argument.replace("lab-", "").strip()
    if lab_label.isdigit():
        heading = f"Pass rates for Lab {lab_label.zfill(2)}:"
    else:
        heading = f"Pass rates for {argument}:"

    lines = [heading]
    for item in pass_rates:
        if not isinstance(item, dict):
            lines.append(f"- {item}")
            continue

        task_name = str(item.get("task", "Unknown task"))
        avg_score = float(item.get("avg_score", 0.0))
        attempts = int(item.get("attempts", 0))
        lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")

    return "\n".join(lines)


def handle_unknown(command: str) -> str:
    """Handle unknown commands."""
    return f"Unknown command: {command}. Type /help for the command list."
