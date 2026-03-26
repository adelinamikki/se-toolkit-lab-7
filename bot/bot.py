import argparse
import sys

from config import BotConfig
from handlers.default import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
    handle_unknown,
)


def run_test(command_text: str) -> str:
    normalized = command_text.strip()

    # Git Bash / MSYS path conversion can turn "/start" into a Windows path.
    if ":\\" in normalized or normalized.lower().startswith("c:/"):
        basename = normalized.replace("\\", "/").split("/")[-1]
        if basename in {"start", "help", "health", "labs", "scores"}:
            normalized = "/" + basename

    if normalized.startswith("/start"):
        return handle_start()
    if normalized.startswith("/help"):
        return handle_help()
    if normalized.startswith("/health"):
        return handle_health()
    if normalized.startswith("/labs"):
        return handle_labs()
    if normalized.startswith("/scores"):
        parts = normalized.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else None
        return handle_scores(arg)

    return handle_unknown(normalized)


def main() -> int:
    parser = argparse.ArgumentParser(description="LMS Telegram bot runner")
    parser.add_argument("--test", dest="test_text", help="Run in test mode with given command text")
    args = parser.parse_args()

    config = BotConfig()  # loads .env.bot.secret by default

    if args.test_text is None:
        print("Telegram transport is not implemented in this scaffold yet.")
        print("Use --test '/start' to run handlers locally.")
        return 0

    # The P0 requirement says test mode should work without BOT_TOKEN
    # so we do not validate BOT_TOKEN here.
    output = run_test(args.test_text)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
