# Application Module Documentation

## Overview
The `app.py` module implements a FastAPI-based web application that serves as the main entry point for the LLM interaction system. It provides an API endpoint for processing user requests, handling various output formats, and implementing error correction.

## API Endpoints

### POST /ask
Main endpoint for processing user requests and generating responses.

**Request:**
- Headers: Standard HTTP headers
- Body: JSON or other supported formats
- Content-Type: application/json (default)

**Response:**
- Content-Type: Varies based on requested format
- Status Codes:
  - 200: Successful response
  - 400: Bad request
  - 500: Internal server error
  - 502: LLM service error

## Request Processing Flow

1. **Request Handling:**
   ```python
   @app.post("/ask")
   async def interpret(request: Request):
       context = {}
       try:
           request_headers = dict(request.headers)
           request_body = await request.body()
   ```

2. **Context Processing:**
   ```python
   context = await handle_user_request(request_headers, request_body)
   ```

3. **Error Handling:**
   ```python
   if context_error:
       return PlainTextResponse("Error: ...", status_code=400)
   ```

4. **LLM Interaction:**
   ```python
   raw_llm_response = await send_prompt_to_llm(simplified_prompt)
   ```

5. **Output Processing:**
   ```python
   universal_representation = parse_llm_output(raw_llm_response, requested_format, context)
   transformer = get_transformer(requested_format)
   transformed_output = transformer.transform(universal_representation, context)
   ```

6. **Validation:**
   ```python
   validation_result = validate_output(transformed_output, requested_format, expected_structure)
   ```

7. **Error Correction:**
   ```python
   if not validation_result.get("valid"):
       error_corrector_output = await correct_output(...)
   ```

8. **Learning:**
   ```python
   learner.learn_from_interaction(interaction_data)
   ```

## Response Format Handling

### JSON Responses
```python
if requested_format == "json":
    return JSONResponse(content=json.loads(transformed_output))
```

### HTML Responses
```python
if requested_format == "html":
    return HTMLResponse(content=transformed_output)
```

### Python Responses
```python
if requested_format == "python":
    return PlainTextResponse(content=transformed_output, media_type="text/x-python")
```

### Plain Text Responses
```python
return PlainTextResponse(content=transformed_output)
```

## Error Handling

### Request Errors
- Missing question
- Invalid JSON
- CSV errors
- Unsupported content type

### LLM Errors
- Service unavailability
- Response format errors
- Timeout errors

### Validation Errors
- Format validation failures
- Structure validation failures
- Type validation failures

### Internal Errors
- JSON parsing errors
- Transformation errors
- Unhandled exceptions

## Middleware

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Logging

### Configuration
```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Log Levels
- DEBUG: Detailed information
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

## Dependencies

### External Libraries
- FastAPI
- Uvicorn
- JSON
- Logging

### Internal Modules
- config
- prompt_handler
- llm_manager
- output_parser
- format_transformer
- validator
- error_corrector
- learner

## Usage Example

### Basic Request
```python
import requests

response = requests.post(
    "http://localhost:5025/ask",
    json={"question": "What is the capital of France?"},
    headers={"Content-Type": "application/json"}
)
```

### With Format Specification
```python
response = requests.post(
    "http://localhost:5025/ask",
    json={
        "question": "List the first 5 prime numbers",
        "format": "json"
    }
)
```

## Best Practices

### Error Handling
1. **Request Validation:**
   - Validate input format
   - Check required fields
   - Handle content types

2. **Response Handling:**
   - Use appropriate status codes
   - Provide meaningful error messages
   - Implement fallback mechanisms

3. **Logging:**
   - Log all important events
   - Include context information
   - Use appropriate log levels

### Performance
1. **Async Operations:**
   - Use async/await
   - Handle timeouts
   - Implement retries

2. **Resource Management:**
   - Close connections
   - Clean up resources
   - Handle memory usage

### Security
1. **Input Validation:**
   - Sanitize input
   - Validate formats
   - Handle malicious input

2. **CORS:**
   - Configure allowed origins
   - Set appropriate headers
   - Handle credentials

## Future Enhancements

1. **API Features:**
   - Additional endpoints
   - Rate limiting
   - Authentication

2. **Error Handling:**
   - More detailed error messages
   - Custom error types
   - Better recovery strategies

3. **Performance:**
   - Caching
   - Load balancing
   - Response compression 