from typing import Optional

from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    BOT_TOKEN: Optional[str] = None
    LMS_API_BASE_URL: Optional[str] = None
    LMS_API_KEY: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    LLM_API_BASE_URL: Optional[str] = None
    LLM_API_MODEL: Optional[str] = None

    class Config:
<<<<<<< HEAD
        env_file = "../.env.bot.secret"
=======
        env_file = ".env.bot.secret"
>>>>>>> d8e6be9aa8cbc10d1f3c49af314f4d1f6eb451b5
        env_file_encoding = "utf-8"
