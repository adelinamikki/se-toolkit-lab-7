from typing import Optional


def handle_start() -> str:
    return "Hello! LMS bot is running. Use /help to see available commands."


def handle_help() -> str:
    return "Available commands:\n/start\n/help\n/health\n/labs\n/scores <lab>"


def handle_health() -> str:
    return "Health check: placeholder OK. Backend integration coming in Task 2."


def handle_labs() -> str:
    return "Labs command placeholder. Real data will be fetched from LMS API in Task 2."


def handle_scores(argument: Optional[str] = None) -> str:
    if not argument:
        return "Usage: /scores <lab-id>"
    return f"Scores command placeholder for lab {argument}."


def handle_unknown(command: str) -> str:
    return f"Unknown command: {command}. Type /help for the command list."