from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    openai_api_token: str
    github_api_token: str

    model_config = SettingsConfigDict(env_file=BASE_DIR / '../.env')


settings = Settings()
