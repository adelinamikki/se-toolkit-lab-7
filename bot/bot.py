import argparse
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import BotConfig
from handlers.default import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
    handle_unknown,
)
from services.intent_router import IntentRouter


def build_start_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with common natural-language prompts for Telegram users."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Available labs",
                    callback_data="prompt:what labs are available?",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Lab 4 scores",
                    callback_data="prompt:show me scores for lab 4",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Lowest pass rate",
                    callback_data="prompt:which lab has the lowest pass rate?",
                )
            ],
        ]
    )


def create_dispatcher() -> Dispatcher:
    """Create Telegram dispatcher with a minimal /start handler."""
    dispatcher = Dispatcher()

    @dispatcher.message(CommandStart())
    async def start_command(message: Message) -> None:
        await message.answer(handle_start(), reply_markup=build_start_keyboard())

    @dispatcher.callback_query()
    async def prompt_button(callback: CallbackQuery) -> None:
        data = callback.data or ""
        if not data.startswith("prompt:"):
            await callback.answer()
            return

        prompt = data.removeprefix("prompt:")
        response_text = IntentRouter(BotConfig()).route(prompt)
        if callback.message is not None:
            await callback.message.answer(response_text, reply_markup=build_start_keyboard())
        await callback.answer()

    return dispatcher


def run_test(command_text: str) -> str:
    """Run a command in test mode.

    Args:
        command_text: The command string (e.g., "/start", "/scores lab-04")

    Returns:
        The handler output as a string.
    """
    normalized = command_text.strip()

    # Git Bash / MSYS path conversion can turn "/start" into a Windows path.
    if ":\\" in normalized or normalized.lower().startswith("c:/"):
        normalized_path = normalized.replace("\\", "/")
        marker = "/Program Files/Git/"
        if marker in normalized_path:
            suffix = normalized_path.split(marker, maxsplit=1)[1]
            parts = suffix.split(maxsplit=1)
            basename = parts[0]
            if basename in {"start", "help", "health", "labs", "scores"}:
                normalized = "/" + basename
                if len(parts) > 1:
                    normalized += " " + parts[1]
        else:
            basename = normalized_path.split("/")[-1]
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

    if normalized.startswith("/"):
        return handle_unknown(normalized)

    router = IntentRouter(BotConfig())
    return router.route(normalized)


def main() -> int:
    """Entry point.

    Supports --test mode for local testing without Telegram transport.
    """
    parser = argparse.ArgumentParser(description="LMS Telegram bot runner")
    parser.add_argument("--test", dest="test_text", help="Run in test mode with given command text")
    args = parser.parse_args()

    config = BotConfig()  # loads .env.bot.secret by default

    if args.test_text is None:
        if config.BOT_TOKEN:
            Bot(token=config.BOT_TOKEN)
            create_dispatcher()
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
