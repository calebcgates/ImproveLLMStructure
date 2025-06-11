# Data Structures Module Documentation

## Overview
The `data_structures.py` module defines the core data structures used throughout the application for representing and processing LLM outputs. The primary structure is the `universal_representation` dictionary, which provides a standardized format for handling different types of content.

## Universal Representation

### Structure
```python
universal_representation = {
    "text_content": None,      # Plain text content
    "json_fields": None,       # Parsed JSON data (dict or list)
    "code_snippets": None,     # List of extracted code snippets (strings)
    "html_content": None,      # HTML content as a string
    "output_structure": None,  # Structure analysis of LLM output (dict)
}
```

### Field Descriptions

#### text_content
- **Type:** `Optional[str]`
- **Purpose:** Stores plain text content from LLM output
- **Usage:** When the output is primarily textual in nature
- **Example:**
  ```python
  "text_content": "This is a plain text response from the LLM."
  ```

#### json_fields
- **Type:** `Optional[Union[dict, list]]`
- **Purpose:** Stores structured data in JSON format
- **Usage:** When the output contains JSON data
- **Example:**
  ```python
  "json_fields": {
      "key": "value",
      "nested": {
          "array": [1, 2, 3]
      }
  }
  ```

#### code_snippets
- **Type:** `Optional[List[str]]`
- **Purpose:** Stores extracted code blocks
- **Usage:** When the output contains programming code
- **Example:**
  ```python
  "code_snippets": [
      "def example_function():\n    return True",
      "class ExampleClass:\n    pass"
  ]
  ```

#### html_content
- **Type:** `Optional[str]`
- **Purpose:** Stores HTML markup
- **Usage:** When the output contains HTML content
- **Example:**
  ```python
  "html_content": "<div><p>Example HTML content</p></div>"
  ```

#### output_structure
- **Type:** `Optional[dict]`
- **Purpose:** Stores analysis of the LLM output structure
- **Usage:** For tracking and analyzing output patterns
- **Example:**
  ```python
  "output_structure": {
      "format": "json",
      "complexity": "high",
      "sections": ["header", "body", "footer"]
  }
  ```

## Usage Guidelines

### Initialization
```python
from data_structures import universal_representation

# Create a new instance
representation = universal_representation.copy()

# Set specific fields
representation["text_content"] = "Example text"
representation["json_fields"] = {"key": "value"}
```

### Best Practices

1. **Field Management:**
   - Initialize all fields as `None`
   - Update only relevant fields
   - Clear unused fields

2. **Data Validation:**
   - Validate field types
   - Check for required fields
   - Handle missing data

3. **Content Organization:**
   - Keep related content together
   - Use appropriate fields
   - Maintain consistency

### Common Operations

1. **Adding Content:**
   ```python
   # Add text content
   representation["text_content"] = "New text content"
   
   # Add JSON data
   representation["json_fields"] = {"new": "data"}
   
   # Add code snippet
   representation["code_snippets"] = ["new_code()"]
   ```

2. **Updating Content:**
   ```python
   # Update existing content
   if representation["text_content"]:
       representation["text_content"] += "\nAdditional text"
   ```

3. **Clearing Content:**
   ```python
   # Clear specific field
   representation["text_content"] = None
   
   # Clear all fields
   for key in representation:
       representation[key] = None
   ```

## Integration

### With Other Modules

1. **Format Transformer:**
   - Uses universal representation for input
   - Transforms content to requested format
   - Returns formatted output

2. **Error Corrector:**
   - Takes universal representation as input
   - Applies corrections
   - Returns corrected representation

3. **Output Parser:**
   - Parses LLM output into universal representation
   - Validates structure
   - Updates fields accordingly

## Future Enhancements

1. **Additional Fields:**
   - Support for more content types
   - Metadata fields
   - Version tracking

2. **Validation:**
   - Type checking
   - Schema validation
   - Content verification

3. **Utilities:**
   - Helper methods
   - Conversion functions
   - Analysis tools 