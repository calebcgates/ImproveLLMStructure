# Configuration Module Documentation

## Overview
The `config.py` module provides centralized configuration settings for the application. It includes settings for LLM API endpoints, default values, error correction parameters, and comprehensive language configurations.

## Configuration Sections

### LLM API Settings
```python
LLM_API_ENDPOINT = "http://localhost:5015/ask"
LLM_API_TIMEOUT = 450  # Timeout for LLM API requests in seconds
```

### Default Settings
```python
DEFAULT_OUTPUT_FORMAT = "plaintext"  # Default output format if not specified
```

### Error Correction Settings
```python
ERROR_CORRECTION_RETRIES = 4  # Number of retries for error correction
```

## Language Configuration

### Structure
The `LANGUAGE_CONFIG` dictionary maps language names to their specific configurations. Each language configuration includes:
- Family classification
- Keywords
- Comment syntax
- File extension
- Optional formatter

### Supported Languages

#### Python
```python
"python": {
    "family": "scripting",
    "keywords": ["def", "class", "import", "for", "while", "if", "else", "try", "except", "finally", "return", "with", "as", "from", "lambda", "yield"],
    "comment_syntax": "#",
    "file_extension": ".py",
    "formatter": "black"
}
```

#### Java
```python
"java": {
    "family": "imperative",
    "keywords": ["public", "class", "static", "void", "int", "String", "if", "else", "for", "while", "try", "catch", "finally", "return", "new", "import", "package"],
    "comment_syntax": "//",
    "file_extension": ".java",
    "formatter": "google-java-format"
}
```

#### JavaScript
```python
"javascript": {
    "family": "scripting",
    "keywords": ["const", "let", "var", "function", "if", "else", "for", "while", "return", "new", "class", "this", "try", "catch", "finally"],
    "comment_syntax": "//",
    "file_extension": ".js",
    "formatter": "prettier"
}
```

#### HTML/JavaScript
```python
"htmljavascript": {
    "family": "frontend",
    "keywords": ["div", "input", "function", "const", "let", "var", "if", "else", "for", "while", "return", "new", "class", "this", "try", "catch", "finally", "<script>", "</script>", "<html>", "</html>", "<head>", "</head>", "<body>", "</body>", "<style>", "</style>", "class", "id", "src", "href", "onclick", "document"],
    "comment_syntax": "//",
    "file_extension": ".html"
}
```

#### HTML
```python
"html": {
    "family": "markup",
    "keywords": ["html", "head", "body", "div", "p", "span", "a", "img", "table", "tr", "td", "th", "ul", "ol", "li", "form", "input", "button", "select", "option"],
    "comment_syntax": "<!-- -->",
    "file_extension": ".html"
}
```

#### CSS
```python
"css": {
    "family": "styling",
    "keywords": ["selector", "property", "value", "color", "background", "font", "margin", "padding", "border", "display", "position", "{", "}", ":", ";"],
    "comment_syntax": "/* */",
    "file_extension": ".css"
}
```

#### SQL
```python
"sql": {
    "family": "data",
    "keywords": ["SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "CREATE", "TABLE", "JOIN", "GROUP BY", "ORDER BY", "AND", "OR", "NOT", "NULL"],
    "comment_syntax": "--",
    "file_extension": ".sql"
}
```

### Additional Languages
- C
- C++
- C#
- Go
- Ruby
- PHP
- Swift
- Kotlin
- R
- Bash
- TypeScript

## Language Families

The configuration uses the following language families:
1. **Scripting**: Python, JavaScript, Ruby, PHP, Bash
2. **Imperative**: Java, C, C++, C#, Go, Swift, Kotlin
3. **Markup**: HTML
4. **Styling**: CSS
5. **Data**: SQL
6. **Frontend**: HTML/JavaScript
7. **Statistical**: R

## Configuration Protection

The module includes a `_deep_freeze` function to prevent accidental modification of the configuration:
```python
def _deep_freeze(data):
    if isinstance(data, dict):
        return {k: _deep_freeze(v) for k, v in data.items()}
    elif isinstance(data, list):
        return tuple(_deep_freeze(x) for x in data)
    return data
```

## Usage Examples

### Accessing Language Configuration
```python
from config import LANGUAGE_CONFIG

# Get Python configuration
python_config = LANGUAGE_CONFIG["python"]

# Get comment syntax for a language
comment_syntax = LANGUAGE_CONFIG["python"]["comment_syntax"]

# Check if a language is supported
is_supported = "python" in LANGUAGE_CONFIG
```

### Using API Settings
```python
from config import LLM_API_ENDPOINT, LLM_API_TIMEOUT

# Use in API calls
response = await make_api_call(
    endpoint=LLM_API_ENDPOINT,
    timeout=LLM_API_TIMEOUT
)
```

## Best Practices

### Configuration Management
1. **Centralization:**
   - Keep all configuration in one place
   - Use clear, descriptive names
   - Document all settings

2. **Modification:**
   - Use the frozen configuration
   - Create copies for modifications
   - Validate changes

3. **Extensibility:**
   - Follow the existing structure
   - Add new languages consistently
   - Update documentation

### Language Configuration
1. **Keywords:**
   - Include essential language keywords
   - Keep lists up to date
   - Consider language versions

2. **Families:**
   - Use consistent family names
   - Group similar languages
   - Document family purposes

3. **Formatters:**
   - Specify standard formatters
   - Include version information
   - Document requirements

## Future Enhancements

1. **Configuration Management:**
   - Environment-based settings
   - Configuration validation
   - Dynamic updates

2. **Language Support:**
   - More language families
   - Additional formatters
   - Version-specific configs

3. **Security:**
   - Encrypted settings
   - Access control
   - Audit logging 