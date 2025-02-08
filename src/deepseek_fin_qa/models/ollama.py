from llama_index.llms.ollama import Ollama

from deepseek_fin_qa.models.base import BaseModelWrapper


class OllamaModel(BaseModelWrapper):
    """Wrapper class for Ollama model."""

    def __init__(self, model_name: str, cache: str | None = ".cache") -> None:
        """Initialize the OllamaModel."""
        super().__init__(model_name, cache)

        self.model = Ollama(
            model=self.model_name,
            request_timeout=120,
            base_url="http://100.100.6.6:11434",
            temperature=0,
        )
