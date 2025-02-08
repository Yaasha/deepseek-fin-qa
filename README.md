# DeepSeek FinQA

This project aims to evaluate the ability of Deepseek R1 distill models in answering financial questions using the `train.json` portion of the [ConvFinQA](https://github.com/czyssrs/ConvFinQA) dataset.

This project contains simple setup for running zero-shot evaluation of LLMs using Ollama and Groq backends, with additional parsing capabilities targeted towards reasoning models.

## Getting Started

1. Clone the repo
```sh
git clone https://github.com/Yaasha/deepseek-fin-qa.git
cd deepseek-fin-qa
```

2. Setup the environment using [uv](https://docs.astral.sh/uv/getting-started/installation/)
```sh
uv sync --frozen
```

3. Run the pipeline
```sh
# Ollama
export BACKEND=ollama
export MODEL=deepseek-r1:14b
export BASE_URL=http://127.0.0.1:11434

uv run scripts/qa.py <PATH_TO_DATASET> <PATH_TO_OUTPUT>
```
```sh
# Groq
export BACKEND=groq
export MODEL=deepseek-r1-distill-llama-70b
export API_KEY=<GROQ_API_KEY>

uv run scripts/qa.py <PATH_TO_DATASET> <PATH_TO_OUTPUT>
```
