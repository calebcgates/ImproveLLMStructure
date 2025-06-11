# Learner Module Documentation

## Overview
The `learner.py` module implements a learning system that improves performance based on interaction data. It logs interactions, updates learning data, and applies learning rules to adjust system behavior based on validation results and context.

## Class: Learner

### Initialization
```python
def __init__(self, log_dir="logs"):
    self.log_dir = log_dir
    if not os.path.exists(self.log_dir):
        os.makedirs(self.log_dir)
    self.learning_data = []  # In-memory store
```

## Main Methods

### learn_from_interaction(interaction_data: dict)
Main method that processes interaction data for learning.

**Parameters:**
- `interaction_data` (dict): Dictionary containing all interaction data including context

**Process:**
1. Logs the interaction
2. Updates learning data
3. Applies learning rules

### _log_interaction(interaction_data: dict)
Logs interaction data to a timestamped file.

**Features:**
- Creates timestamped log files
- Stores data in JSON format
- Handles file writing errors

### _update_learning_data(interaction_data: dict)
Updates internal learning data store.

**Features:**
- Appends interaction data to memory
- Maintains history of interactions
- Ready for future persistence

### _apply_learning(interaction_data: dict)
Applies learning rules based on interaction data.

**Learning Rules:**
1. **Confidence Adjustment:**
   - Increases confidence on successful validation
   - Decreases confidence on failed validation
   - Adjusts both input and output structure confidence

2. **CSV Input Handling:**
   - Reduces confidence for consistently misinterpreted CSV
   - Considers validation error types

3. **Format Deduction:**
   - Evaluates LLM format suggestions
   - Adjusts confidence based on accuracy
   - Handles format type mismatches

## Learning Rules

### Rule 1: Validation-Based Confidence
```python
if validation_result:  # Success
    input_structure["confidence"] = min(1.0, input_structure["confidence"] + 0.05)
    output_structure["confidence"] = min(1.0, output_structure["confidence"] + 0.05)
else:  # Failure
    input_structure["confidence"] = max(0.0, input_structure["confidence"] - 0.1)
    output_structure["confidence"] = max(0.0, output_structure["confidence"] - 0.1)
```

### Rule 2: CSV Input Handling
```python
if input_structure["input_structure_type"] == "csv_input" and not validation_result["valid"]:
    if validation_result["error_type"] != "JSONDecodeError":
        input_structure["confidence"] = max(0.0, input_structure["confidence"] - 0.1)
```

### Rule 3: Format Deduction
```python
if "llm_format_deduction_response" in context:
    # Evaluates LLM format suggestions against actual output
    # Adjusts confidence based on accuracy
```

## Usage Example
```python
from learner import Learner

# Initialize learner
learner = Learner()

# Example interaction data
interaction_data = {
    "context": {
        "input_structure": {
            "input_structure_type": "csv_input",
            "confidence": 0.9
        },
        "prompt_text": "Convert CSV to JSON",
        "requested_format": "json"
    },
    "universal_representation": {
        "output_structure": {
            "output_structure_type": "json_like_output",
            "confidence": 0.8
        }
    },
    "validation_result": True
}

# Process interaction
learner.learn_from_interaction(interaction_data)
```

## Data Structure

### Interaction Data Format
```python
{
    "context": {
        "input_structure": dict,
        "prompt_text": str,
        "requested_format": str,
        "output_intent": str,
        "llm_format_deduction_response": str
    },
    "universal_representation": {
        "output_structure": dict,
        "text_content": str,
        "json_fields": dict,
        "code_snippets": list,
        "html_content": str
    },
    "validation_result": Union[bool, dict],
    "error": str
}
```

## Dependencies
- `json`: For data serialization
- `logging`: For logging
- `os`: For file operations
- `datetime`: For timestamp generation

## Future Enhancements
1. **Advanced Learning Rules:**
   - Prompt template improvement
   - Parsing strategy adjustment
   - Format-specific optimizations

2. **Persistence:**
   - Database integration
   - File-based storage
   - Learning data export

3. **Analysis:**
   - Performance metrics
   - Error pattern detection
   - Confidence trend analysis 