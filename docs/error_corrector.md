# Error Corrector Module Documentation

## Overview
The `error_corrector.py` module provides functionality for correcting errors in transformed outputs. It uses a combination of heuristic correction and iterative prompting with LLMs to fix validation errors in various formats.

## Main Functions

### correct_output
```python
async def correct_output(
    universal_representation: dict,
    requested_format: str,
    raw_llm_response: str,
    context: dict,
    validation_result: Union[bool, Dict]
) -> str
```

Attempts to correct errors in transformed output using two approaches:
1. Heuristic correction
2. Iterative prompting with LLM

**Parameters:**
- `universal_representation` (dict): The current representation of the data
- `requested_format` (str): The desired output format
- `raw_llm_response` (str): The original LLM response
- `context` (dict): Additional context for correction
- `validation_result` (Union[bool, Dict]): Result from validation

**Returns:**
- Corrected output as string

**Process Flow:**
1. Attempts heuristic correction first
2. If heuristic correction fails, proceeds with iterative prompting
3. Uses format-specific correction prompts
4. Validates corrections after each attempt
5. Returns best attempt after multiple retries

## Helper Functions

### _heuristic_correction
```python
def _heuristic_correction(
    universal_representation: dict,
    requested_format: str
) -> Optional[dict]
```

Applies heuristic-based corrections to the universal representation.

**Features:**
- JSON-specific corrections
- Text content to JSON conversion
- Error handling for JSON parsing

### Format-Specific Correction Prompts

#### _construct_json_structure_prompt
```python
def _construct_json_structure_prompt(
    validation_result: Union[bool, Dict],
    raw_llm_response: str,
    context: dict
) -> str
```

Constructs prompts for correcting JSON array/object structure issues.

#### _construct_json_correction_prompt
```python
def _construct_json_correction_prompt(
    validation_result: Union[bool, Dict],
    raw_llm_response: str
) -> str
```

Handles JSON syntax and validation errors.

#### _construct_html_correction_prompt
```python
def _construct_html_correction_prompt(
    validation_result: Union[bool, Dict],
    raw_llm_response: str
) -> str
```

Addresses HTML structure and parsing errors.

#### _construct_python_correction_prompt
```python
def _construct_python_correction_prompt(
    validation_result: Union[bool, Dict],
    raw_llm_response: str
) -> str
```

Handles Python syntax and validation errors.

#### _construct_format_correction_prompt
```python
def _construct_format_correction_prompt(
    raw_llm_response: str,
    requested_format: str,
    last_error_message: str,
    validation_result: Union[bool, Dict]
) -> str
```

General-purpose format correction prompt constructor.

## Usage Example
```python
from error_corrector import correct_output

# Example usage
universal_representation = {
    "json_fields": None,
    "text_content": '{"key": "value"}',
    "code_snippets": None,
    "html_content": None
}

context = {
    "output_intent": "code_only",
    "prompt_text": "Create a JSON object"
}

validation_result = {
    "valid": False,
    "error_type": "JSONStructureError",
    "message": "Expected a JSON object"
}

corrected_output = await correct_output(
    universal_representation,
    "json",
    raw_llm_response,
    context,
    validation_result
)
```

## Error Types Handled

### JSON Errors
- JSONDecodeError
- JSONStructureError
- Array/Object structure mismatches

### HTML Errors
- HTMLStructureError
- HTMLParseError
- Tag nesting issues

### Python Errors
- PythonSyntaxError
- PythonValidationError
- Code structure issues

## Dependencies
- `json`: For JSON processing
- `logging`: For logging
- `llm_manager`: For LLM interaction
- `format_transformer`: For format transformation
- `output_parser`: For parsing LLM output
- `validator`: For output validation
- `config`: For configuration settings

## Best Practices

### Error Handling
1. **Validation:**
   - Validate after each correction attempt
   - Use specific error types for targeted correction
   - Handle both boolean and dictionary validation results

2. **Correction Strategy:**
   - Try heuristic correction first
   - Use format-specific prompts
   - Implement fallback mechanisms

3. **Logging:**
   - Log correction attempts
   - Track success/failure
   - Record error messages

### Performance Considerations
1. **Retry Limits:**
   - Use configurable retry count
   - Avoid infinite loops
   - Return best attempt after max retries

2. **Resource Usage:**
   - Minimize LLM calls
   - Use efficient data structures
   - Implement early exit conditions

## Future Enhancements
1. **Additional Formats:**
   - Support more output formats
   - Add format-specific heuristics
   - Implement custom validators

2. **Improved Heuristics:**
   - Enhanced pattern matching
   - Machine learning-based corrections
   - Context-aware fixes

3. **Better Error Handling:**
   - More detailed error reporting
   - Custom exception types
   - Recovery strategies 