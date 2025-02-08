from llama_index.llms.groq import Groq

from deepseek_fin_qa.models.base import BaseModelWrapper
from deepseek_fin_qa.settings import settings


class GroqModel(BaseModelWrapper):
    """Wrapper class for Groq model."""

    def __init__(self, model_name: str, cache: str | None = ".cache") -> None:
        """Initialize the GroqModel."""
        super().__init__(model_name, cache)

        self.model = Groq(model=self.model_name, api_key=settings.api_key)
