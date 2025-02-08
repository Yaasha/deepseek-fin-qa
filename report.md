# Evaluation report

## Introduction

The aim of this project is to evaluate the feasibility of using the newly released Deepseek R1 distilled models for the task of financial question answering on the `train.json` portion of the [ConvFinQA](https://github.com/czyssrs/ConvFinQA) dataset.


The model selected for evaluation was a self-hosted `deepseek-r1:14b` using Ollama. This model is only 9GBs in size and can be easily hosted locally on modern PCs. This makes it an interesting alternative to more costly frontier LLMs.

## Approach

A simplified representation of the approach used in this pipeline is represented in the flow chart below:

![Pipeline flow chart](images/flow_chart.png)

Additionally, the pipeline also uses logging and caching, making the process fault-tolerant and speeding up the development process.

### Prompt

The aim of this evaluation is to see how the latest reasoning models perform on this type of financial question answering. For prompting, I have used a zero-shot approach with minimal examples of expected responses, since these kinds of prompts perform better than few-shot or chain-of-thought prompting, as per the Deepseek technical report. The model does most of this automatically through the reasoning process. Additionally, the prompt includes instructions on how to avoid some common edge-cases and issues identified during testing. The full prompt used is available in `src/deepseek_fin_qa/prompts.py`.

In addition to the static system prompt, the model is also receiving a dynamic user prompt, which includes the question and question context (constructed based on the `pre_text`, `post_text` and `table_ori` fields of the dataset).

For multi-step Q&As (a feature specific to the ConvFinQA dataset), the questions are processed sequentially with the input and output of each question added to the LLMs chat history. This means that the model has access to preceding questions when answering follow-up questions (within a single context).

### Pre-processing

In order to keep results comparable to the original dataset, no pre-processing that would alter the shape of the dataset was applied. The only pre-processing is combining the context data into a single string and converting the Python table from the context into a Markdown table so that it can be better understood by the LLM (this improved the performance considerably).

### Post-processing

A common issue that I experienced during development and that is also well documented online, is that the Deepseek model often does not return responses in the requested JSON output. This made it harder for me to parse the responses in order to properly evaluate the results. I have applied the following post-processing steps in order to get as much structured data out of the LLM as possible, but this proved to be a big issue with the distilled model and I have not found a definitive solution yet.

Parsing steps:
1. Ignore model reasoning by skipping past the `</think>`
2. Skip additional output by only parsing content formatted within curly brackets
3. For float values, parse values using regex to avoid issues with extra characters (e.g. `$30million`)

## Evaluation

### Metrics selection

In line with the original ConvFinQA paper, I have chosen to measure the accuracy of the answer value (usually in the form of a float value or "yes"/"no" string) and the accuracy of the program code used to calculate this value based on provided data (e.g. `subtract(4,add(6,8))` would evaluate to value of `-10`).

This choice of metrics allows me to easily compare my results directly with the models evaluated in the CovFinQA paper.

In order to properly estimate if the answer value and the program match between the target and LLM answers. I am applying the following steps when evaluating the equivalency of these values:

#### Answer execution value
1. Strip any extra characters
2. Find the rounding factor used in the target answer
3. Apply rounding factor to the LLM answer
4. Convert values to floats and evaluate equivalency using `math.isclose`
5. Ignore signs if working with percentage values (as the sign of a difference is ambiguous)
6. Account for inconsistent rounding of the target answer

#### Answer program
1. Strip all whitespace from the program
2. Convert constants references to values
3. Safely evaluate the program to get a program result
4. Programs are equivalent if they yield the same result (within floating point error)
5. Account for percentage values being on scale 0-100 or 0-1

### Results

The total evaluation of the `train.json` dataset using the `deepseek-r1:14b` with Ollama on RTX4070Ti took about 16 hours to complete.

The achieved execution accuracy was `69.99%` and program accuracy was `70.32%`. This places the Deepseek model ahead of all of the other evaluated models, with the exception of `FinQANet-Gold` (which uses additional supporting facts). However, the model is still far below the human target of 89.44% and 86.34%, respectively.

Below are the collected results in comparison to the original ConFinQA results with the addition of model sizes.

| Baselines                     | Exe Acc | Prog Acc |
|-------------------------------|---------|----------|
| Deepseek R1 14B               |**69.99**|**70.32** |
| GPT-2(medium)                 | 58.19   | 57.00    |
| T-5(large)                    | 58.66   | 57.05    |
| FinQANet (BERT-base)          | 55.03   | 54.57    |
| FinQANet (BERT-large)         | 61.14   | 60.55    |
| FinQANet (RoBERTa-base)       | 64.95   | 64.16    |
| FinQANet (RoBERTa-large)      | 68.90   | 68.24    |
| FinQANet-Gold (RoBERTa-large) | 77.32   | 76.46    |
| Human Expert Performance      | 89.44   | 86.34    |
| General Crowd Performance     | 46.90   | 45.52    |

### Conclusion

The modern, distilled reasoning model like Deepseek R1 14B seems to outperform historical state-of-the art models out-of-the-box with minimal setup. This is especially impressive considering this evaluation was done in a very short time-frame with model running on consumer GPU.


The main issues I have noticed while evaluating the data was that the model often returned invalid data in its output. This seems to drag the average accuracy down and it might be possible that more work spent on prompt engineering and answer parsing might alleviate this issue.

One strong suite I have noticed with the Deepseek model was its execution result precision. As seen in the results, the model actually performs quite well in giving the correct number in its answer, but struggles to show how it got to this number in the required step-by-step format. This is possibly a limitation of the reasoning chain, which happens before the answer is generated and is not performed in a structured format.


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