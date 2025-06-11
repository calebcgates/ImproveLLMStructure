# Format Transformer Module Documentation

## Overview
The `format_transformer.py` module provides a flexible system for transforming data between different formats. It uses a class hierarchy of transformers to handle various programming languages, markup languages, and data formats.

## Class Hierarchy

### Base Classes

#### FormatTransformer (ABC)
Abstract base class defining the interface for all transformers.

**Methods:**
- `transform(universal_representation: dict, context: dict) -> str`
- `can_handle(requested_format: str) -> bool`
- `get_supported_formats() -> List[str]`

#### Intermediate Abstract Classes
1. **ScriptingLanguageTransformer**
   - Handles scripting languages (Python, JavaScript, etc.)
   - Inherits from FormatTransformer

2. **ImperativeLanguageTransformer**
   - Handles imperative languages (Java, C++, etc.)
   - Inherits from FormatTransformer

3. **MarkupLanguageTransformer**
   - Handles markup languages (HTML, XML, etc.)
   - Inherits from FormatTransformer

4. **DataOrientedLanguageTransformer**
   - Handles data-oriented languages (SQL, etc.)
   - Inherits from FormatTransformer

5. **StylingLanguageTransformer**
   - Handles styling languages (CSS, etc.)
   - Inherits from FormatTransformer

6. **FrontendLanguageTransformer**
   - Handles frontend technologies
   - Inherits from FormatTransformer

7. **StatisticalLanguageTransformer**
   - Handles statistical languages (R, etc.)
   - Inherits from FormatTransformer

8. **FunctionalLanguageTransformer**
   - Handles functional languages
   - Inherits from FormatTransformer

## Concrete Transformers

### Basic Format Transformers

#### PlainTextTransformer
Handles plain text transformation.

**Features:**
- Returns stripped text content
- No special formatting

#### JSONTransformer
Handles JSON transformation.

**Features:**
- Converts various data types to JSON
- Handles nested structures
- Provides error handling
- Pretty printing with indentation

#### HTMLTransformer
Handles HTML transformation.

**Features:**
- Converts JSON to HTML tables
- Handles lists and dictionaries
- Basic text escaping
- Fallback mechanisms

### Language-Specific Transformers

#### PythonTransformer
Handles Python code transformation.

**Features:**
- Code-only mode
- Code with explanation mode
- Combines code and text

#### JavaTransformer
Handles Java code transformation.

**Features:**
- Code-only mode
- Basic text to comment conversion
- Code snippet handling

#### JavascriptTransformer
Handles JavaScript code transformation.

**Features:**
- Code-only mode
- Text to comment conversion
- Code snippet handling

#### HTMLJavascriptTransformer
Handles combined HTML and JavaScript.

**Features:**
- Combines HTML and JavaScript
- Basic template structure

### Other Language Transformers
- CTransformer
- CppTransformer
- CSharpTransformer
- GoTransformer
- RubyTransformer
- PHPTransformer
- SwiftTransformer
- KotlinTransformer
- RTransformer
- BashTransformer
- TypescriptTransformer
- CSSTransformer
- SQLTransformer

## Utility Functions

### get_transformer(requested_format: str) -> Optional[FormatTransformer]
Factory function to get the appropriate transformer for a requested format.

**Parameters:**
- `requested_format` (str): The desired output format

**Returns:**
- Appropriate transformer instance or None

## Usage Example
```python
from format_transformer import get_transformer

# Get transformer for JSON
transformer = get_transformer("json")

# Transform data
universal_representation = {
    "json_fields": {"key": "value"},
    "text_content": None,
    "code_snippets": None,
    "html_content": None
}
context = {"output_intent": "code_only"}

# Transform
result = transformer.transform(universal_representation, context)
```

## Data Structure

### Universal Representation
```python
{
    "json_fields": Union[dict, list, None],
    "text_content": Optional[str],
    "code_snippets": Optional[List[str]],
    "html_content": Optional[str]
}
```

### Context
```python
{
    "output_intent": str,  # e.g., "code_only"
    "requested_format": str,
    # Additional context as needed
}
```

## Dependencies
- `json`: For JSON processing
- `logging`: For logging
- `abc`: For abstract base classes
- `typing`: For type hints
- `config`: For language configuration

## Error Handling
- JSON parsing errors
- Type conversion errors
- Missing data handling
- Fallback mechanisms

## Best Practices
1. **Format Validation:**
   - Validate input data
   - Handle missing fields
   - Provide fallback values

2. **Error Handling:**
   - Catch and log exceptions
   - Provide meaningful error messages
   - Use fallback mechanisms

3. **Code Organization:**
   - Use inheritance for common functionality
   - Implement specific transformers for each format
   - Follow the interface contract 