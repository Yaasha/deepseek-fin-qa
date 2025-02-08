import math

from deepseek_fin_qa.utils.evaluation import (
    evaluate_program,
    get_execution_match,
    get_program_output_match,
    list_to_markdown_table,
)


def test_evaluate_program() -> None:
    """Test safe evaluation of a mathematical expression."""
    # Test case 1: Empty code
    code = ""
    result = evaluate_program(code)
    assert result is math.nan

    # Test case 2: Valid code
    code = "add(5,subtract(10,3))"
    result = evaluate_program(code)
    assert result == 12

    # Test case 3: Bool output
    code = "greater(10,5)"
    result = evaluate_program(code)
    assert result == "yes"


def test_list_to_markdown_table() -> None:
    """Test conversion of a list of lists into a Markdown table."""
    # Test case 1: Empty data
    data = []
    result = list_to_markdown_table(data)
    assert result == ""

    # Test case 2: Non-empty data
    data = [["Name", "Age"], ["John", "25"], ["Alice", "30"]]
    result = list_to_markdown_table(data)
    expected_output = "| Name | Age |\n| --- | --- |\n| John | 25 |\n| Alice | 30 |\n"
    assert result == expected_output


def test_get_execution_match() -> None:
    """Test matching of execution values."""
    # Test case 1: Matching string values
    target_value = "yes"
    llm_value = "yes"
    result = get_execution_match(target_value, llm_value)
    assert result == True

    # Test case 2: Matching percentage values
    target_value = "4.3%"
    llm_value = "4.34562"
    result = get_execution_match(target_value, llm_value)
    assert result == True

    # Test case 2: Non-matching values
    target_value = "4.3%"
    llm_value = "4.39562"
    result = get_execution_match(target_value, llm_value)
    assert result == False


def test_get_program_output_match() -> None:
    """Test matching of program output."""
    # Test case 1: Matching values
    target_value = 10.5
    llm_value = 10.5
    result = get_program_output_match(target_value, llm_value)
    assert result == True

    # Test case 2: Non-matching values
    target_value = 10.5
    llm_value = 20.0
    result = get_program_output_match(target_value, llm_value)
    assert result == False

    # Test case 3: Matching bool values
    target_value = "yes"
    llm_value = "yes"
    result = get_program_output_match(target_value, llm_value)
    assert result == True

    # Test case 4: Non-matching bool values
    target_value = "yes"
    llm_value = 4.5
    result = get_program_output_match(target_value, llm_value)
    assert result == False
