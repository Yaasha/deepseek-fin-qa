from pathlib import Path
from typing import TYPE_CHECKING

from llama_index.core.llms import ChatMessage
from llama_index.core.output_parsers import PydanticOutputParser

from deepseek_fin_qa.prompts import FINQA_SYSTEM_PROMPT, FINQA_USER_PROMPT
from deepseek_fin_qa.schemas.qa import Answer, FinQA
from deepseek_fin_qa.utils.cache import ChatCache

if TYPE_CHECKING:
    from llama_index.core.llms.function_calling import FunctionCallingLLM


class ReasoningOutputParser(PydanticOutputParser):
    """Custom output parser for reasoning models."""

    def parse(self, text: str) -> Answer:
        """Parse the output text of a reasoning model.

        Deepseek includes <think></think> tags in the output text. This method
        tries to find the part of the output that includes the expected JSON and applies
        the default parsing.

        Args:
            text (str): The output text to parse.

        Returns:
            Parsed output.

        """
        if "```json" in text:
            text = text[text.find("```json") :]
        elif "{" in text:
            text = text[text.rfind("{") :]
        elif "</think>" in text:
            text = text[text.find("</think>") :]
        return super().parse(text)


class BaseModelWrapper:
    """Wrapper class for LLamaIndex model."""

    def __init__(self, model_name: str, cache: str | None = ".cache") -> None:
        """Initialize the BaseModelWrapper.

        Args:
            model_name (str): The name of the model.
            cache (str | None, optional): The cache directory. Defaults to ".cache".

        """
        self.model_name = model_name
        self.parser = ReasoningOutputParser(Answer)

        if cache:
            self.cache = ChatCache(
                Path(cache) / f"{self.model_name}.json"
            )  # Initialize cache
        else:
            self.cache = None

        self.model: FunctionCallingLLM

    def answer_questions(self, fin_qa: FinQA) -> list[Answer]:
        """Answer a list of questions.

        Args:
            fin_qa (FinQA): The list of questions and context.

        Returns:
            list[Answer]: The list of answers.

        """
        messages = [
            ChatMessage(
                role="system",
                content=FINQA_SYSTEM_PROMPT,
            ),
        ]

        answers = []
        for qa in fin_qa:
            messages.append(
                ChatMessage(
                    role="user",
                    content=FINQA_USER_PROMPT.format(
                        question=qa.question,
                        context=fin_qa.context,
                    ),
                )
            )

            response = None
            if self.cache:
                # Check if response is cached
                response = self.cache.get(str(messages))

            if response is None:
                response = self.model.chat(messages)  # Get response from model
                if self.cache:
                    self.cache.set(str(messages), str(response))  # Cache the response

            # Parse the response
            answers.append(self.parser.parse(str(response)))
            messages.append(
                ChatMessage(
                    # Add assistant message to messages for next iteration
                    role="assistant",
                    content=str(response),
                )
            )
        return answers
