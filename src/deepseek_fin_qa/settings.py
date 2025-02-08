import dotenv
from pydantic_settings import BaseSettings

dotenv.load_dotenv()


class Settings(BaseSettings):
    """Settings for the project."""

    backend: str = "ollama"
    model: str = "deepseek-r1:14b"

    api_key: str | None = None


settings = Settings()
