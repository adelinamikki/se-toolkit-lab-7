from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parent.parent


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env.bot.secret",
        env_file_encoding="utf-8",
    )

    BOT_TOKEN: Optional[str] = None
    LMS_API_BASE_URL: Optional[str] = None
    LMS_API_KEY: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    LLM_API_BASE_URL: Optional[str] = None
    LLM_API_MODEL: Optional[str] = None
