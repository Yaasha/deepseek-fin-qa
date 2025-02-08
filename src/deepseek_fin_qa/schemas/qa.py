import json
import math
from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel

from deepseek_fin_qa.log import LOG
from deepseek_fin_qa.schemas.metrics import Accuracy, Score
from deepseek_fin_qa.utils.evaluation import (
    evaluate_program,
    get_execution_match,
    get_program_output_match,
    list_to_markdown_table,
)


class Answer(BaseModel):
    """Answer to a question."""

    value: str | float = "nan"
    program: str = "nan"

    @property
    def stripped_program(self) -> str:
        """Return the program without any special characters."""
        program = self.program
        program = program.replace(" ", "")
        program = program.replace("const_m", "-")
        program = program.replace("const_", "")
        program = program.replace("$", "")
        return program.replace("%", "")

    @property
    def program_output(self) -> float:
        """Evaluate the program and return the output."""
        return evaluate_program(self.stripped_program)


class QA(BaseModel):
    """Question and answer with optional LLM answer."""

    question: str
    target_answer: Answer
    llm_answer: Answer | None = None

    @property
    def score(self) -> Score:
        """Calculate the score for the QA pair."""
        if self.llm_answer is None:
            LOG.warning("Score not available for QA pair without LLM answer.")
            return Score(execution=False, program=False)

        return Score(
            execution=get_execution_match(
                str(self.target_answer.value), str(self.llm_answer.value)
            ),
            program=get_program_output_match(
                self.target_answer.program_output, self.llm_answer.program_output
            ),
        )


class FinQA(BaseModel):
    """Financial QA data with a list of questions."""

    qa_list: list[QA]

    pre_text: str
    post_text: str
    table: list[list[str]]

    def __iter__(self) -> Iterator[QA]:
        """Iterate over the QA pairs."""
        yield from self.qa_list

    def __len__(self) -> int:
        """Return the number of QA pairs."""
        return len(self.qa_list)

    @property
    def context(self) -> str:
        """Return the context of the QA data."""
        return f"""
        {self.pre_text}

        {list_to_markdown_table(self.table)}

        {self.post_text}
        """


class FinQADataset(BaseModel):
    """Financial QA dataset with a list of FinQA data."""

    finqa_list: list[FinQA]

    def __iter__(self) -> Iterator[FinQA]:
        """Iterate over the FinQA data."""
        yield from self.finqa_list

    def __len__(self) -> int:
        """Return the number of FinQA data."""
        return len(self.finqa_list)

    @classmethod
    def from_file(cls, file_path: str) -> "FinQADataset":
        """Load a FinQA dataset from a JSON file."""
        # Load JSON data from the file and parse it into a dictionary
        with Path(file_path).open("r") as f:
            data = json.load(f)

        finqa_list = []
        for fin_qa in data:
            # Create QA object for each data key starting with "qa"
            qa_list = [
                QA(
                    question=fin_qa[key]["question"],
                    target_answer=Answer(
                        value=fin_qa[key]["answer"],
                        program=fin_qa[key]["program_re"],
                    ),
                )
                for key in fin_qa
                if key.startswith("qa")
            ]

            # Combine QA objects into a FinQA object with context data
            finqa_list.append(
                FinQA(
                    pre_text="\n".join(fin_qa["pre_text"]),
                    post_text="\n".join(fin_qa["post_text"]),
                    table=fin_qa["table_ori"],
                    qa_list=qa_list,
                )
            )

        return cls(finqa_list=finqa_list)

    @property
    def score(self) -> Accuracy:
        """Calculate the mean accuracy of the answered FinQA dataset."""
        execution_score = 0
        program_score = 0
        n = 0

        for fin_qa in self:
            for qa in fin_qa:
                if qa.llm_answer:
                    execution_score += qa.score.execution
                    program_score += qa.score.program
                    n += 1

        return Accuracy(execution=execution_score / n, program=program_score / n)
