# Local Model Module Documentation

## Overview
The `local_model.py` module implements a FastAPI server that provides an interface to a local MLX language model. It handles model loading, text generation, and provides a REST API endpoint for making queries to the model.

## API Endpoints

### POST /ask
Handles question requests and generates answers using the local MLX model.

**Request Body:**
```json
{
    "question": "string",
    "max_tokens": "integer (optional)"
}
```

**Response:**
```json
{
    "answer": "string"
}
```

## Configuration

### CORS Settings
The server is configured to accept requests from any origin:
```python
origins = ["*"]
```

### Model Loading
- The model is loaded from the directory containing the script
- Uses MLX's `load` function to initialize the model and tokenizer
- Handles various loading errors gracefully

## Main Components

### QuestionRequest Model
Pydantic model for request validation:
```python
class QuestionRequest(BaseModel):
    question: str
    max_tokens: Optional[int] = None
```

### Ask Endpoint
The main endpoint that processes questions and generates responses:

1. **Prompt Processing:**
   - Applies chat template if available
   - Falls back to raw prompt if template application fails
   - Handles tokenization and decoding

2. **Response Generation:**
   - Runs model generation in a thread pool
   - Configurable max tokens (default: 128000)
   - Error handling for generation failures

## Error Handling

The module implements comprehensive error handling for:
1. **Model Loading:**
   - Missing model files
   - Incompatible model versions
   - Unexpected loading errors

2. **Request Processing:**
   - Invalid request formats
   - Template application errors
   - Generation failures

## Usage Example

### Starting the Server
```bash
python local_model.py
```
The server starts on `http://0.0.0.0:5015`

### Making Requests
```python
import requests

response = requests.post(
    "http://localhost:5015/ask",
    json={
        "question": "What is machine learning?",
        "max_tokens": 1000
    }
)
print(response.json()["answer"])
```

## Dependencies
- `fastapi`: Web framework
- `pydantic`: Data validation
- `mlx_lm`: MLX language model interface
- `uvicorn`: ASGI server
- `traceback`: Error tracking

## Model Configuration

### Model Loading
The module attempts to load the model from the current directory:
```python
MODEL_PATH = CURRENT_DIR
model, tokenizer = load(MODEL_PATH)
```

### Chat Template
If available, the tokenizer's chat template is applied to format the prompt:
```python
if hasattr(tokenizer, 'chat_template') and tokenizer.chat_template:
    messages = [{"role": "user", "content": current_prompt}]
    prompt_from_template = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
```

## Error Responses

The API returns appropriate HTTP status codes:
- `200`: Successful generation
- `500`: Generation failure
- `422`: Invalid request format

## Logging
The module includes comprehensive logging:
- Model loading status
- Prompt processing
- Generation progress
- Error details 