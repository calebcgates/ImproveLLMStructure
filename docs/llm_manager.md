# LLM Manager Module Documentation

## Overview
The `llm_manager.py` module provides functionality for communicating with a Language Model (LLM) API. It handles asynchronous requests, error handling, and response processing for interactions with the LLM service.

## Main Function

### send_prompt_to_llm(prompt: str) -> str
Asynchronously sends a prompt to the LLM API and returns the raw response.

**Parameters:**
- `prompt` (str): The prompt string to send to the LLM

**Returns:**
- Success: The raw LLM response string
- Error: An error message prefixed with "Error: "

## Error Handling

The function implements comprehensive error handling for various scenarios:

### 1. HTTP Errors
- **TimeoutException:**
  - Occurs when the request times out
  - Returns: "Error: Timeout while waiting for LLM response."

- **RequestError:**
  - General request errors
  - Returns: "Error: Request error communicating with LLM API: {error}"

- **HTTPStatusError:**
  - HTTP status code errors
  - Special handling for 422 (Missing question)
  - Returns: Appropriate error message based on status code

### 2. Response Processing Errors
- **JSONDecodeError:**
  - Occurs when response is not valid JSON
  - Returns: "Error: Could not decode JSON response from LLM API."

- **Missing Answer Field:**
  - Occurs when response JSON lacks "answer" field
  - Returns: "Error: LLM response missing 'answer' field."

### 3. Unexpected Errors
- Catches any unhandled exceptions
- Returns: "Error: An unexpected error occurred: {error}"

## Configuration

The module uses configuration from `config.py`:
- `LLM_API_ENDPOINT`: The endpoint URL for the LLM API
- `LLM_API_TIMEOUT`: Timeout duration for API requests

## Request Format

### Headers
```python
headers = {
    "Content-Type": "application/json"
}
```

### Request Body
```python
data = {
    "question": prompt
}
```

## Usage Example
```python
from llm_manager import send_prompt_to_llm

async def process_prompt():
    prompt = "What is machine learning?"
    response = await send_prompt_to_llm(prompt)
    
    if response.startswith("Error:"):
        print(f"Error occurred: {response}")
    else:
        print(f"LLM response: {response}")
```

## Dependencies
- `httpx`: For asynchronous HTTP requests
- `json`: For JSON processing
- `asyncio`: For asynchronous operations
- `logging`: For error logging
- `config`: For configuration constants

## Logging

The module uses Python's logging system to record:
- API request errors
- Response processing errors
- Unexpected errors

Example log messages:
```python
logger.error("Error: Timeout while waiting for LLM response.")
logger.error(f"Error: Request error communicating with LLM API: {e}")
logger.error("Error: Could not decode JSON response from LLM API.")
```

## Best Practices

1. **Error Handling:**
   - All errors are caught and logged
   - Error messages are prefixed with "Error: " for consistent handling
   - Specific error types have specific messages

2. **Async Operations:**
   - Uses `httpx.AsyncClient` for non-blocking requests
   - Properly manages async context

3. **Response Validation:**
   - Checks for required "answer" field
   - Validates JSON response format
   - Provides meaningful error messages

4. **Configuration:**
   - Uses external configuration for flexibility
   - Supports timeout configuration
   - Configurable API endpoint 