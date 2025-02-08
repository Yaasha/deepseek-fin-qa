import dotenv
from pydantic_settings import BaseSettings

dotenv.load_dotenv()


class Settings(BaseSettings):
    """Settings for the project."""

    backend: str = "ollama"
    model: str = "deepseek-r1:14b"

    base_url: str | None = None
    api_key: str | None = None


settings = Settings()
