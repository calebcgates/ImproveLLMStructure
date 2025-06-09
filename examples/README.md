# API Curl Request Examples

This document provides examples of how to use the API through curl requests. The API endpoint is available at `http://localhost:5025/ask` and accepts POST requests with JSON payloads.

## Basic Structure

All requests should follow this basic structure:
```bash
curl -X POST \
  http://localhost:5025/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Your question here",
    "output_format": "desired_format"
  }'
```

## Available Output Formats

The API supports the following output formats:
- `json`: Returns JSON data
- `html`: Returns HTML content
- `python`: Returns Python code
- `text`: Returns plain text

## Example Requests

### 1. Basic JSON Output
```bash
curl -X POST \
  http://localhost:5025/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Convert this text to json: Name: John Smith, Age: 35, Occupation: Software Engineer, Skills: Python, JavaScript, SQL",
    "output_format": "json"
  }'
```

Expected output:
```json
{
  "Name": "John Smith",
  "Age": 35,
  "Occupation": "Software Engineer",
  "Skills": ["Python", "JavaScript", "SQL"]
}
```

### 2. HTML Output Format
```bash
curl -X POST \
  http://localhost:5025/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Create an HTML table for a weekly schedule with Monday to Friday, 9 AM to 5 PM",
    "output_format": "html"
  }'
```

### 3. Python Code Output
```bash
curl -X POST \
  http://localhost:5025/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Write a Python function that calculates the Fibonacci sequence",
    "output_format": "python"
  }'
```

### 4. Plain Text Output
```bash
curl -X POST \
  http://localhost:5025/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Write a short story about a robot learning to paint",
    "output_format": "text"
  }'
```

### 5. JSON Array Output
```bash
curl -X POST \
  http://localhost:5025/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Create a JSON array of 5 different programming languages with their year of creation",
    "output_format": "json"
  }'
```

### 6. Error Case - Missing Question
```bash
curl -X POST \
  http://localhost:5025/ask \
  -H "Content-Type: application/json" \
  -d '{
    "output_format": "json"
  }'
```

Expected error:
```
Error: The question is missing from your request.
```

### 7. Error Case - Invalid JSON
```bash
curl -X POST \
  http://localhost:5025/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Convert this to JSON",
    "output_format": "json"
    "missing": "comma"
  }'
```

Expected error:
```
Error: Invalid JSON provided in request.
```

### 8. Complex JSON Object
```bash
curl -X POST \
  http://localhost:5025/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Create a JSON object representing a company with departments, employees, and their salaries",
    "output_format": "json"
  }'
```

### 9. HTML with CSS Styling
```bash
curl -X POST \
  http://localhost:5025/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Create a responsive HTML page with CSS for a product catalog",
    "output_format": "html"
  }'
```

### 10. Python with Data Processing
```bash
curl -X POST \
  http://localhost:5025/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Write a Python script that processes a CSV file and creates a summary report",
    "output_format": "python"
  }'
```

## Error Handling

The API provides detailed error messages for various scenarios:
- Missing question: Returns 400 Bad Request
- Invalid JSON: Returns 400 Bad Request
- LLM errors: Returns 502 Bad Gateway
- Internal server errors: Returns 500 Internal Server Error

## Best Practices

1. Always include the `Content-Type: application/json` header
2. Ensure your JSON payload is properly formatted
3. Specify the desired output format in the request
4. Handle potential errors in your client code
5. For large responses, consider implementing proper timeout handling

## Notes

- The API runs on port 5025 by default
- All responses are UTF-8 encoded
- The API includes CORS support for cross-origin requests
- The API includes built-in error correction and validation 