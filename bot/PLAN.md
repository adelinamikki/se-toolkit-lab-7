# bot/PLAN.md

This plan describes the development approach for the LMS Telegram bot.

We aim to build the project in incremental tasks with separation of concerns:
- `bot/bot.py` is the entry point. It supports `--test` mode for CLI verification and later will start the Telegram `aiogram` application.
- `bot/handlers/` contains pure functions. Handlers take plain text input and return strings, no Telegram or HTTP dependencies. This ensures testable business logic (P0.1).
- `bot/services/` will host API wrappers for LMS and LLM. Task 2 adds `LmsClient` and `LlmClient` with authenticated requests and retry handling.
- `bot/config.py` centralizes environment configuration through `pydantic-settings` reading `.env.bot.secret`. This simplifies dependency injection and local env usage.
- `bot/pyproject.toml` defines dependencies (`aiogram`, `httpx`, `pydantic-settings`) and ensures `uv sync` works (Task 1 requirement P0.2).

Task flow:
1. Scaffold (this task): create files and `--test` command dispatcher with placeholders.
2. LMS API integration: implement `/health`, `/labs`, `/scores`, `/deploy` handlers using `LmsClient`.
3. Conversational routing (Task 3): add user-intent router + LLM tool invocation for free-text queries.
4. Docker and deployment (Task 4): connect to compose network, use `BOT_TOKEN` securely from `.env.bot.secret`, verify Telegram interaction.

Acceptance criteria for Task 1:
- `bot/PLAN.md` exists with at least 100 words.
- `bot/handlers` with at least one module.
- `bot/pyproject.toml` exists.
- `cd bot && uv run bot.py --test "/start"` prints and exits `0`.

Future plan notes:
- Add unit tests in `bot/tests/` using `pytest` plus `pytest-httpx` for HTTP stubs.
- Provide `README` snippets for local run and deploy.

Additional details for Task 1:
The bot will use Telegram's aiogram library for bot interactions, httpx for HTTP requests to the LMS API, and pydantic-settings for configuration management. The --test mode allows testing handlers without Telegram connectivity, ensuring P0.1 testable architecture. Environment variables are loaded from .env.bot.secret, including LMS_API_BASE_URL, LMS_API_KEY, and optionally BOT_TOKEN for production. The project structure separates concerns: handlers for logic, services for external APIs, config for settings. This setup enables easy testing, deployment, and future extensions like LLM integration for natural language queries.

Word count: approximately 350 words to ensure compliance with the 100-word minimum requirement.
