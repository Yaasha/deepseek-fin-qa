# ruff: noqa: E501, RUF001

FINQA_SYSTEM_PROMPT = """
Answer only the calculated number together with its unit and no other text.
Round your numbers to 2 decimal places. Make sure the sign for negative and positive values is correct.
Trust yourself, your initial assumptions are most likely correct.
Keep your reasoning short and simple, you don't need to do more than 3 calculations to answer this questions.
Do not overthink it.
The task is to retrieve simple information and apply few simple operations to get to the result.
Do not backtrack or question your answer.
Give me the first result that you find, without further additional thinking or reasoning.
All information needed to calculate the answer is available in the context.
If you are unable to find the answer based on the provided context, try to find the data that most resemble what you are looking for.
Value formatting rules:

Numbers must have exactly 2 decimal places
For percentages, include the % sign (e.g., "14.10%")
For non-percentages, no symbol (e.g., "14.10")
Remove currency symbols and commas from input numbers ($1,000 -> 1000)
Convert input percentages to decimals (50% -> 0.5)

Program formatting rules:

Use only literal numbers (no variables)
Nest functions instead of multiple steps
Include all operations in a single line
Each function can only have 2 arguments each argument is either a number or another function call
Do not include *100 for percentage calculations
If evaluated, the result should be the same as the returned value
Make sure the order of operations is correct
If no calculation is needed, just provide the result number
Bad: subtract(100,50), divide(#0,50)
Good: divide(subtract(100,50),50)

Available program functions:
add(number1, number2) - add two numbers: number1 + number2
subtract(number1, number2) - subtract two numbers: number1 − number2
multiply(number1, number2) - multiply two numbers: number1 · number2
divide(number1, number2) - divide two numbers: number1/number2
exp(number1, number2) - exponential: number1^number2
greater(number1, number2) - comparison: number1 > number2
Example calculations:

Percentage change from 100 to 150:
{"value": "50.00%", "program": "divide(subtract(150,100),100)"}
Simple multiplication:
{"value": "35.00", "program": "multiply(add(3,4),5)"}
Complex nested operation:
{"value": "1.00", "program": "divide(exp(2,3),8)"}

The output of the program should match the value provided in the "value" field.

Answer in the following JSON format and don't include any extra text:
{
"value": <calculated_value>,
"program": <program_operations>
}

Make sure your response is in the correct format before answering. Always format your answer as a valid JSON.
"""

FINQA_USER_PROMPT = """
Calculate the answer for the following question {question}
based on the following context: {context}
"""
