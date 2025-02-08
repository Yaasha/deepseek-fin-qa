from pathlib import Path

import tqdm
import typer
from pydantic import ValidationError

from deepseek_fin_qa.log import LOG
from deepseek_fin_qa.models.groq import GroqModel
from deepseek_fin_qa.models.ollama import OllamaModel
from deepseek_fin_qa.schemas.qa import FinQADataset
from deepseek_fin_qa.settings import settings

MODEL_BACKENDS = {
    "ollama": OllamaModel,
    "groq": GroqModel,
}


def process_data(src: str, out: str) -> None:
    """Answer questions from a dataset.

    Args:
        src (str): Path to the dataset file.
        out (str): Path to the output file.

    """
    # Prepare the dataset and model
    dataset = FinQADataset.from_file(src)
    model = MODEL_BACKENDS[settings.backend](model_name=settings.model)

    answered_dataset = FinQADataset(finqa_list=[])

    # Answer the questions
    for fin_qa in tqdm.tqdm(list(dataset)):
        try:
            answers = model.answer_questions(fin_qa)
            for qa, answer in zip(fin_qa, answers, strict=False):
                LOG.debug(f"Question: {qa.question}")
                LOG.debug(f"Context: {fin_qa.context}")
                LOG.debug(f"Target: {qa.target_answer}")
                LOG.debug(f"Answer: {answer}")
                qa.llm_answer = answer
            answered_dataset.finqa_list.append(fin_qa)
        except ValidationError as ex:
            LOG.warning(ex)

    with Path(out).open("w") as f:
        f.write(answered_dataset.model_dump_json())

    LOG.info(f"Score: {answered_dataset.score}")


if __name__ == "__main__":
    typer.run(process_data)
