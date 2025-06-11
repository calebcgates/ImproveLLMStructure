# Prompt Handler Module Documentation

## Overview
The `prompt_handler.py` module provides functionality for handling user requests, parsing input data, deducing output formats and intents, and constructing appropriate prompts for the LLM. It supports various input formats and content types, including JSON, form data, CSV, XML, and plaintext.

## Main Functions

### handle_user_request(request_headers: dict, request_body: bytes) -> dict
Asynchronously handles user requests, parses input, deduces output format & intent, constructs prompts, and manages context.

**Parameters:**
- `request_headers` (dict): HTTP request headers
- `request_body` (bytes): Raw request body

**Returns:**
A context dictionary containing:
- `raw_input_data` (str): Decoded request body
- `input_format_type` (str): Content type of input
- `prompt_text` (str): Extracted prompt text
- `requested_format` (str): Output format requested
- `instructions` (list): Additional instructions
- `simplified_prompt` (str): Final constructed prompt
- `llm_format_deduction_response` (str): LLM's format deduction response
- `input_structure` (dict): Analysis of input structure
- `output_intent` (str): Detected output intent
- `error` (str): Any error message

## Input Processing

### Supported Content Types
- `application/json`: JSON formatted input
- `application/x-www-form-urlencoded`: Form data
- `text/plain`: Plain text input
- `text/csv`: CSV formatted input
- `application/xml`/`text/xml`: XML formatted input
- `application/octet-stream`: Treated as plaintext

### Input Parsing
1. **JSON Input:**
   - Extracts `question` and `output_format` fields
   - Validates JSON structure
   - Falls back to plaintext if invalid

2. **Form Data:**
   - Parses URL-encoded form data
   - Extracts `question` and `output_format` fields
   - Falls back to plaintext if parsing fails

3. **CSV Input:**
   - Validates CSV structure
   - Defaults to JSON output format
   - Constructs conversion prompt

4. **Plaintext/Other:**
   - Uses raw input as prompt text
   - Deduces format and intent

## Format and Intent Deduction

### Format Deduction Process
1. **Explicit Format:**
   - Checks for format in input data
   - Uses content type hints

2. **Agent Prompt Analysis:**
   - Analyzes prompt for format indicators
   - Uses LLM for format deduction if needed

3. **Heuristic Analysis:**
   - Checks input structure
   - Looks for format-specific keywords
   - Uses confidence scores

4. **Default Fallback:**
   - Uses `DEFAULT_OUTPUT_FORMAT` if no format detected

### Intent Deduction
1. **Explicit Intent:**
   - Checks for intent parameter
   - Supports: `code_only`, `code_with_explanation`

2. **Keyword Analysis:**
   - Analyzes prompt for intent indicators
   - Checks for explanation/comment keywords

3. **Default Intent:**
   - Uses `code_with_explanation` as default

## Prompt Construction

### Format-Specific Prompts
1. **JSON:**
   - Requests raw JSON output
   - Excludes surrounding text and markdown

2. **HTML:**
   - Generates HTML structure
   - Excludes full HTML document tags

3. **Python:**
   - `code_only`: Returns executable code only
   - `code_with_explanation`: Includes comments and explanations

4. **Plaintext:**
   - Uses raw prompt with input structure context

## Helper Functions

### _analyze_for_agent_prompt(prompt_text: str) -> tuple[Optional[str], Optional[str]]
Analyzes prompt text for format and intent indicators.

### _construct_prompt(prompt_text, requested_format, output_intent, input_structure_info)
Constructs the final prompt based on format and intent.

## Usage Example
```python
from prompt_handler import handle_user_request

# Example request
headers = {
    "content-type": "application/json"
}
body = b'{"question": "Convert this to JSON", "output_format": "json"}'

# Handle request
context = await handle_user_request(headers, body)
```

## Dependencies
- `json`: For JSON parsing
- `logging`: For logging
- `urllib.parse`: For form data parsing
- `llm_manager`: For LLM interaction
- `config`: For configuration constants
- `structure`: For structure analysis 