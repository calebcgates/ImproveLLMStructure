# Output Parser Module Documentation

## Overview
The `output_parser.py` module provides functionality for parsing and cleaning LLM (Large Language Model) outputs into various formats including JSON, HTML, Python code, and plaintext. It includes robust error handling, format-specific parsing, and fallback mechanisms to ensure valid output structures.

## Main Functions

### parse_llm_output(raw_llm_response: str, requested_format: str, context: dict) -> dict
Main function that parses the raw LLM response into the requested format.

**Parameters:**
- `raw_llm_response` (str): Raw response from the LLM
- `requested_format` (str): Desired output format
- `context` (dict): Additional context for parsing

**Returns:**
A dictionary containing the parsed output in the universal representation format.

## Format-Specific Parsing

### _parse_as_json(cleaned_response: str, parsed_output: dict, context: dict) -> None
Parses the response as JSON, handling both object and array structures.

**Features:**
- Extracts and validates JSON content
- Handles object vs. array discrepancies
- Provides fallback mechanisms
- Sets error flags for incorrect structures

### _parse_as_html(cleaned_response: str, parsed_output: dict, context: dict) -> None
Parses the response as HTML, ensuring valid HTML structure.

**Features:**
- Validates HTML using BeautifulSoup
- Provides minimal HTML fallback
- Handles missing tags gracefully

### _parse_as_python(cleaned_response: str, parsed_output: dict, context: dict) -> None
Parses the response as Python code, considering output intent.

**Features:**
- Extracts Python code snippets
- Handles code-only vs. code-with-explanation intents
- Provides fallback for missing code

## Helper Functions

### _cleanup_common_artifacts(text: str) -> str
Removes common artifacts from LLM responses:
- Code fences (```)
- Result wrappers
- AI disclaimers
- Extra whitespace

### _extract_and_parse_json(text: str) -> Optional[Dict[str, Any]]
Robustly extracts and parses JSON from text:
- Handles nested structures
- Removes code fences
- Validates JSON syntax

### extract_json_robust(text: str) -> Optional[Dict[str, Any]]
Advanced JSON extraction:
- Scans for balanced braces/brackets
- Handles both objects and arrays
- Multiple parsing attempts

### _minimal_html(original_text: str) -> str
Creates minimal HTML structure:
- Escapes special characters
- Wraps content in basic HTML tags
- Provides fallback structure

### _minimal_python(original_text: str) -> str
Creates minimal Python code structure:
- Includes original text as comments
- Provides placeholder function
- Maintains valid Python syntax

## Error Handling

The module implements several error handling mechanisms:
1. **Format Validation:**
   - Validates output against requested format
   - Sets appropriate error flags
   - Provides fallback structures

2. **Structure Analysis:**
   - Analyzes output structure
   - Detects format mismatches
   - Triggers error correction

3. **Fallback Mechanisms:**
   - Minimal HTML for invalid HTML
   - Placeholder Python code
   - Plaintext fallback for unknown formats

## Usage Example
```python
from output_parser import parse_llm_output

# Example usage
raw_response = '{"name": "John", "age": 30}'
context = {
    "output_intent": "code_only",
    "prompt_text": "Create a JSON object"
}

# Parse the output
parsed_output = parse_llm_output(
    raw_llm_response=raw_response,
    requested_format="json",
    context=context
)
```

## Dependencies
- `json`: For JSON parsing
- `logging`: For logging
- `bs4.BeautifulSoup`: For HTML parsing
- `re`: For regular expressions
- `data_structures`: For universal representation
- `structure`: For structure analysis

## Output Structure
The parsed output follows a universal representation format that includes:
- Format-specific content (json_fields, html_content, code_snippets)
- Text content for plaintext or explanations
- Output structure analysis
- Error flags if applicable
- Metadata about the parsing process 