## Evaluation Report

## Introduction

The aim of this project is to evaluate the feasibility of using the newly released DeepSeek R1 distilled models for financial question answering on the `train.json` portion of the [ConvFinQA](https://github.com/czyssrs/ConvFinQA) dataset.

The model selected for evaluation was a self-hosted `deepseek-r1:14b` using Ollama. This model is only 9GB in size and can be easily hosted locally on modern PCs, making it an interesting alternative to more costly frontier LLMs.

## Approach

A simplified representation of the approach used in this pipeline is shown in the flow chart below:

![Pipeline flow chart](images/flow_chart.png)

Additionally, the pipeline includes logging and caching, making the process fault-tolerant and improving development speed.

### Prompting

The goal of this evaluation is to assess how the latest reasoning models perform on financial question answering. I used a **zero-shot prompting approach** with minimal examples of expected responses, as DeepSeek's technical report suggests that this performs better than few-shot or chain-of-thought prompting. The model handles most of the reasoning process automatically. The prompt also includes instructions to mitigate common edge cases and issues identified during testing. The full prompt used is available in `src/deepseek_fin_qa/prompts.py`.

In addition to the static system prompt, the model receives a **dynamic user prompt** containing the **question and context** (constructed from the `pre_text`, `post_text`, and `table_ori` fields of the dataset).

For **multi-step Q&As**, a feature specific to ConvFinQA, questions are processed sequentially, with both the input and output of each question added to the LLM's chat history. This ensures that the model has access to previous questions when answering follow-ups within the same context.

### Pre-processing

To keep results comparable to the original dataset, no pre-processing was applied that would alter the dataset structure. The only pre-processing step was **combining context fields into a single string** and **converting tables into Markdown format**, which improved LLM performance significantly.

### Post-processing

One issue I encountered, which is well documented online, is that DeepSeek models often fail to return responses in the requested JSON format. This made it difficult to parse responses for evaluation. To extract as much structured data as possible, I applied the following post-processing steps:

1. Ignore model reasoning by skipping past the `</think>` tag.
2. Extract only content formatted within curly brackets.
3. Parse float values using regex to remove extra characters (e.g., `$30 million`).

Despite these steps, structured output remained a significant issue with the distilled model, and I have not yet found a definitive solution.

## Evaluation

### Metrics Selection

In line with the original ConvFinQA paper, I measured:

1. **Execution Accuracy** (`Exe Acc`): Whether the numerical answer (typically a float or `"yes"/"no"`) matches the target value.
2. **Program Accuracy** (`Prog Acc`): Whether the program used to compute the answer is correct based on the provided data (e.g., `subtract(4, add(6,8))` should yield `-10`).

This metric choice allows for direct comparison with the results reported in the ConvFinQA paper.

To determine if the LLM answer matches the target, I applied the following evaluation steps:

#### Answer Execution Value

1. Strip any extra characters.
2. Identify the rounding factor used in the target answer.
3. Apply the same rounding to the LLM-generated answer.
4. Convert values to floats and check equivalency using `math.isclose`.
5. Ignore signs for percentage values (since the sign of a difference is ambiguous).
6. Account for inconsistencies in target answer rounding.

#### Answer Program

1. Normalize whitespace in the program.
2. Convert constant references to actual values.
3. Safely execute the program to compute the expected result.
4. Consider programs equivalent if they produce the same result (within floating-point error).
5. Account for percentage values being on a 0-100 or 0-1 scale.

## Results

### Performance Overview

The full evaluation of `train.json` using `deepseek-r1:14b` with Ollama on an RTX 4070 Ti took approximately 16 hours to complete.

- **Execution Accuracy (`Exe Acc`)**: **69.99%**
- **Program Accuracy (`Prog Acc`)**: **70.32%**

### Comparison to ConvFinQA Baselines

| Model                         | Exe Acc | Prog Acc |
|--------------------------------|---------|----------|
| **Deepseek R1 14B**           | **69.99%** | **70.32%** |
| GPT-2 (medium)                 | 58.19%  | 57.00%  |
| T-5 (large)                    | 58.66%  | 57.05%  |
| FinQANet (BERT-base)           | 55.03%  | 54.57%  |
| FinQANet (BERT-large)          | 61.14%  | 60.55%  |
| FinQANet (RoBERTa-base)        | 64.95%  | 64.16%  |
| FinQANet (RoBERTa-large)       | 68.90%  | 68.24%  |
| FinQANet-Gold (RoBERTa-large)  | 77.32%  | 76.46%  |
| Human Expert Performance       | 89.44%  | 86.34%  |
| General Crowd Performance      | 46.90%  | 45.52%  |

DeepSeek R1 14B outperforms all models except **FinQANet-Gold**, which benefits from additional supporting facts. However, it still lags behind human performance.

## Conclusion

The modern, distilled reasoning model like Deepseek R1 14B seems to outperform historical state-of-the art models **out-of-the-box with minimal setup**. This is especially impressive considering that the evaluation pipeline was developed in a short time frame and executed on consumer hardware.

### Key Observations

1. **Frequent invalid output formatting:**  
   - The model often fails to return valid JSON, which makes parsing difficult.
   - Improved prompt engineering and post-processing may help mitigate this.

2. **Strong numerical accuracy, weaker reasoning trace:**  
   - The model frequently produces correct numerical answers but struggles to generate a reasoning chain that matches the required step-by-step format.
   - This suggests that the model's reasoning process occurs before answer generation and is not structured.

3. **Potential for improvement through parsing refinements:**  
   - Additional work on structured output extraction may significantly improve overall accuracy.
   - Ensuring better alignment between reasoning steps and answer generation could improve program accuracy.

## Evaluation Examples

### Example 1: Correct answer
```
Question: what was the percentage change of unrecognized tax benefits at year end between 2017 and 2018?

Target answer:  value='33%'      program='divide(subtract(463, 348), 348)'
LLM answer:     value='32.97%'   program='divide(subtract(463,348),348)'
```

### Example 2: Incorrect answer
```
Question: what portion of the total shares subject to outstanding awards is under the 2009 global incentive plan?
Target answer:  value='70.1%'   program='divide(5923147, add(2530454, 5923147))'
LLM answer:     value='29.93%'  program='multiply(divide(2530454, add(2530454,5923147)), 100)'
```

### Example 3: Correct execution, incorrect program due to percentage conversion
```
Question: what percentage of doors in the wholesale segment as of april 2 , 2016 where in the europe geography?
        
Target answer:  value='42%'     program='divide(5625, 13502)'
LLM answer:     value='41.67%'  program='multiply(divide(5625,13502),100)'
```

### Example 4: Correct answer, incorrect target value
```
Question: what was the difference in percentage return for lilly compared to the s&p 500 for the five years ended dec-18?

Target answer:  value=''            program='subtract(divide(subtract(259.88, const_100), const_100), divide(subtract(150.33, const_100), const_100))'
LLM answer:     value='109.55%'     program='subtract(divide(subtract(259.88,100),100),divide(subtract(150.33,100),100))'
```