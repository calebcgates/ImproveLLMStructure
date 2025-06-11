# Validator Module Documentation

## Overview
The `validator.py` module provides functionality for validating different types of output formats, including JSON, HTML, Python code, and plaintext. It ensures that the output meets the expected format requirements and structure.

## Functions

### validate_output(transformed_output: str, requested_format: str, expected_structure: Optional[str] = None) -> Union[bool, Dict]
Main validation function that routes the validation to the appropriate format-specific validator.

**Parameters:**
- `transformed_output` (str): The output string to validate
- `requested_format` (str): The format the output should be in
- `expected_structure` (Optional[str]): For JSON, specifies whether the output should be an "object" or "array"

**Returns:**
- `True` if valid
- Or a dictionary containing:
  - `valid` (bool): False
  - `error_type` (str): Type of error encountered
  - `message` (str): Error description
  - `fallback_ok` (bool, optional): Indicates if the output can still be treated as valid despite issues

### validate_json(output: str, expected_structure: Optional[str] = None) -> Union[bool, Dict]
Validates if a string is valid JSON and optionally checks its structure.

**Parameters:**
- `output` (str): The string to validate
- `expected_structure` (Optional[str]): "object" or "array"

**Returns:**
- `True` if valid
- Or a dictionary with error details including:
  - `valid` (bool): False
  - `error_type` (str): Type of error (JSONDecodeError or JSONStructureError)
  - `message` (str): Error description
  - Additional fields for JSONDecodeError: `line`, `column`, `position`

### validate_html(output: str) -> Union[bool, Dict]
Performs basic HTML validation using BeautifulSoup.

**Parameters:**
- `output` (str): The HTML string to validate

**Returns:**
- `True` if valid HTML with at least one tag
- Or a dictionary with error details including:
  - `valid` (bool): False
  - `error_type` (str): Type of error (HTMLStructureError or HTMLParseError)
  - `message` (str): Error description
  - `fallback_ok` (bool): True, allowing 200 OK fallback

### validate_python(output: str) -> Union[bool, Dict]
Performs basic Python code validation by checking for syntax errors.

**Parameters:**
- `output` (str): The Python code to validate

**Returns:**
- `True` if valid Python syntax
- Or a dictionary with error details including:
  - `valid` (bool): False
  - `error_type` (str): Type of error (PythonSyntaxError or PythonValidationError)
  - `message` (str): Error description
  - Additional fields for syntax errors: `line`, `offset`

## Usage Example
```python
from validator import validate_output

# Validate JSON
result = validate_output(
    transformed_output='{"key": "value"}',
    requested_format="json",
    expected_structure="object"
)

# Validate HTML
result = validate_output(
    transformed_output="<div>Hello World</div>",
    requested_format="html"
)

# Validate Python code
result = validate_output(
    transformed_output="def hello(): print('world')",
    requested_format="python"
)
```

## Error Handling
The module provides detailed error information when validation fails, including:
- Specific error types for different validation failures
- Descriptive error messages
- Line numbers and positions for syntax errors
- Fallback options for certain formats (like HTML)

## Dependencies
- `json`: For JSON validation
- `logging`: For logging validation results
- `bs4.BeautifulSoup`: For HTML validation (imported locally) 