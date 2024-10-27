from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    openai_api_token: str
    openai_model: str
    github_api_token: str
    exclude_extensions: str | tuple[str, ...] = ('.gitignore',)
    skip_integration_tests: bool = False

    @field_validator('exclude_extensions', mode='before')
    @classmethod
    def convert_exclude_extensions(cls, value):
        if isinstance(value, str):
            return tuple(value.split(' '))
        return value

    model_config = SettingsConfigDict(env_file=BASE_DIR / '../.env', extra='allow')


settings = Settings()
