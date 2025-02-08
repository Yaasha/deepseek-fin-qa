import math
import re
from math import ceil, floor
from typing import Literal

from deepseek_fin_qa.log import LOG


def str_to_float(value: str) -> float:
    """Convert a string to a float using regex matching."""
    num_regex = re.compile(r"[-+]?\d*\.?\d+")
    match = num_regex.search(value)

    if match:
        return float(match.group())

    LOG.warning(f"Failed to convert string to float: {value}")
    return math.nan


def evaluate_program(code: str) -> float | str:
    """Safe evaluation of a mathematical expression."""
    # Find operation that can be evaluated
    op_regex = re.compile(
        r"(add|subtract|multiply|divide|greater|exp)\(([-\d.]+,[-\d.]+)\)"
    )
    match = op_regex.search(code)

    while match:
        # Parse operation and operands
        operation = match.group(1)
        operands = match.group(2)
        num1, num2 = map(str_to_float, operands.split(","))

        # Evaluate operation
        result = ""
        if operation == "add":
            result = num1 + num2
        elif operation == "subtract":
            result = num1 - num2
        elif operation == "multiply":
            result = num1 * num2
        elif operation == "divide":
            result = num1 / num2
        elif operation == "exp":
            result = num1**num2
        # Some operations expect a string result
        elif operation == "greater":
            return "yes" if num1 > num2 else "no"

        # Replace operation with result and move to next operation
        code = code.replace(match.group(), str(result))
        match = op_regex.search(code)

    return str_to_float(code)


def list_to_markdown_table(data: list[list[str]]) -> str:
    """Convert a list of lists into a Markdown table."""
    if not data:
        return ""

    # Extract headers and rows
    headers = data[0]  # First row as headers
    rows = data[1:]  # Remaining data

    # Create Markdown table format
    markdown = "| " + " | ".join(headers) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in rows:
        markdown += "| " + " | ".join(map(str, row)) + " |\n"

    return markdown


def float_round(
    num: float, places: int = 0, direction: Literal[floor, ceil] = floor
) -> float:
    """Round a float number to the nearest place."""
    return direction(num * (10**places)) / float(10**places)


def get_execution_match(target_value: str, llm_value: str) -> bool:
    """Check if the target and LLM values match accounting for formatting."""
    # Handle bool values
    if target_value in ["yes", "no"]:
        llm_value = llm_value.replace("false", "no").replace("true", "yes")
        return target_value == llm_value

    # Sign for percentage values is ambiguous as question asks for difference
    if target_value.endswith("%"):
        target_value = target_value.strip("-")
        llm_value = llm_value.strip("-")

    # Strip punctuation and spaces from both values
    target_value = target_value.replace(
        "%", "").replace(",", "").replace(" ", "")
    llm_value = llm_value.replace("%", "").replace(",", "").replace(" ", "")

    # Round the llm value to match the target value's precision
    target_rounding = len(target_value.split(
        ".")[1]) if "." in target_value else 0

    llm_value_f = str_to_float(llm_value)
    target_value_f = str_to_float(target_value)

    if math.isnan(llm_value_f) or math.isnan(target_value_f):
        return llm_value_f is target_value_f

    # The rounding in dataset is not consistent
    # so we need to check multiple rounding options
    return (
        math.isclose(target_value_f, float_round(
            llm_value_f, target_rounding, ceil))
        or math.isclose(target_value_f,
                        float_round(llm_value_f, target_rounding, floor))
    )


def get_program_output_match(target_value: str | float, llm_value: str | float) -> bool:
    """Check if the target and LLM program outputs match accounting for formatting."""
    if isinstance(target_value, str) or isinstance(llm_value, str):
        return target_value == llm_value

    # Check if the values are equal, accounting for percentage formatting
    return (
        math.isclose(target_value, llm_value)
        or math.isclose(target_value, llm_value * 100)
        or math.isclose(target_value * 100, llm_value)
    )
