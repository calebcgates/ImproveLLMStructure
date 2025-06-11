# Structure Module Documentation

## Overview
The `structure.py` module provides a `StructureAnalyzer` class that analyzes and determines the structure of both input and output text. It supports various formats including JSON, HTML, Python code, CSV, XML, and plaintext. The analyzer uses heuristics and format-specific validation to determine the structure type and provides confidence scores for its analysis.

## Class: StructureAnalyzer

### Methods

#### analyze_input_structure(input_text: str, content_type: str) -> Dict
Analyzes the structure of user input text based on content type and heuristics.

**Parameters:**
- `input_text` (str): The raw user input text
- `content_type` (str): The Content-Type header of the input request

**Returns:**
A dictionary containing:
- `input_structure_type` (str): Type of structure detected
- `confidence` (float): Confidence score (0.0 to 1.0)
- `features` (dict): Structure-specific features
- `metadata` (dict): Additional format-specific data

**Supported Input Types:**
- JSON (`application/json`)
- CSV (`text/csv`)
- Form URL-encoded (`application/x-www-form-urlencoded`)
- XML (`application/xml`, `text/xml`)
- Plain text (`text/plain`)
- Other formats

#### analyze_output_structure(output_text: str, requested_format: str) -> Dict
Analyzes the structure of LLM output text based on the requested format.

**Parameters:**
- `output_text` (str): The raw LLM output text
- `requested_format` (str): The requested output format

**Returns:**
A dictionary containing:
- `output_structure_type` (str): Type of structure detected
- `confidence` (float): Confidence score (0.0 to 1.0)
- `features` (dict): Structure-specific features
- `metadata` (dict): Additional format-specific data

**Supported Output Formats:**
- JSON
- HTML
- Python code
- Plaintext

### Helper Methods

#### _sanitize_for_json(text: str) -> str
Removes code fences, trailing '%', and extra whitespace from text that might be JSON.

#### _extract_python_code_heuristically(text: str) -> List[str]
Extracts Python code snippets from text using heuristics.

#### _is_json_like(text: str) -> bool
Checks if text appears to be JSON-like in structure.

#### _is_code_like(text: str) -> bool
Determines if text appears to be code-like based on keywords and structure.

#### _extract_code_keywords(text: str) -> List[str]
Extracts programming language keywords from text.

#### _is_html_like(text: str) -> bool
Checks if text appears to be HTML-like in structure.

#### learn_from_interaction(input_structure: Dict, output_structure: Dict, validation_result: Union[Dict, bool], context: Dict)
Updates the analyzer's knowledge based on interaction results.

## Usage Example
```python
from structure import StructureAnalyzer

# Create analyzer instance
analyzer = StructureAnalyzer()

# Analyze input structure
input_structure = analyzer.analyze_input_structure(
    input_text='{"name": "John", "age": 30}',
    content_type="application/json"
)

# Analyze output structure
output_structure = analyzer.analyze_output_structure(
    output_text='<div>Hello World</div>',
    requested_format="html"
)
```

## Structure Types

### Input Structure Types
- `json_input`: Valid JSON input
- `json_like_text_input`: JSON-like but invalid
- `csv_input`: CSV formatted input
- `form_urlencoded_input`: Form URL-encoded data
- `xml_input`: XML formatted input
- `potentially_tabular_text_input`: Text that appears to be tabular
- `potentially_list_text_input`: Text that appears to be a list
- `code_like_text_input`: Text that appears to be code
- `unstructured_text_input`: Plain text without clear structure
- `other_input_type`: Other input types

### Output Structure Types
- `valid_json_output`: Valid JSON output
- `json_like_output`: JSON-like but invalid
- `invalid_json_output`: Invalid JSON
- `html_table_output`: HTML with table structure
- `html_list_output`: HTML with list structure
- `html_paragraph_output`: HTML with paragraph structure
- `generic_html_output`: Generic HTML output
- `html_parsing_failed_output`: Failed HTML parsing
- `python_code_output`: Valid Python code
- `no_python_code_output`: No Python code detected
- `plaintext_list_output`: Plaintext in list format
- `plaintext_table_like_output`: Plaintext in table-like format
- `plaintext_paragraph_output`: Plaintext in paragraph format

## Dependencies
- `json`: For JSON parsing
- `logging`: For logging analysis results
- `bs4.BeautifulSoup`: For HTML parsing
- `re`: For regular expression matching 