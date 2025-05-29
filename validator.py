
import json
import logging
import re
from typing import Optional, Dict, Union

logger = logging.getLogger(__name__)

def validate_output(transformed_output: str, requested_format: str, expected_structure: Optional[str] = None) -> Union[bool, Dict]:
    """
    Validates the transformed output based on the requested format.  Optionally
    checks for expected JSON structure (object vs. array).

    Args:
        transformed_output: The output string to validate.
        requested_format: The format the output should be in.
        expected_structure: Optional.  For JSON, "object" or "array".

    Returns:
        - True if valid
        - OR a dictionary with at least:
            {
                "valid": False,
                "error_type": str,
                "message": str,
                # Optionally "fallback_ok": True if you still want to treat it as 200 OK
            }
    """
    try:
        if requested_format == "json":
            result = validate_json(transformed_output, expected_structure)
            logger.info(f"JSON validation result: {result}")
            return result
        elif requested_format == "html":
            result = validate_html(transformed_output)
            logger.info(f"HTML validation result: {result}")
            return result
        elif requested_format == "python":
            result = validate_python(transformed_output)
            logger.info(f"Python validation result: {result}")
            return result
        elif requested_format == "plaintext":
            # Plain text is always considered valid
            logger.info("Plaintext validation result: True")
            return True
        else:
            logger.warning(f"Unknown format for validation: {requested_format}")
            result =  {
                "valid": False,
                "error_type": "UnknownFormat",
                "message": f"Unknown format for validation: {requested_format}",
            }
            logger.info(f"Unknown format validation result: {result}")
            return result
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}", exc_info=True)
        result = {
            "valid": False,
            "error_type": "UnexpectedError",
            "message": str(e),
        }
        logger.info(f"Unexpected error during validation result: {result}")
        return result

def validate_json(output: str, expected_structure: Optional[str] = None) -> Union[bool, Dict]:
    """
    Validates if the given string is valid JSON, and optionally checks
    if it's an object or an array.

    Args:
        output: The string to validate.
        expected_structure: Optional. "object" or "array".

    Returns:
        True if valid, or a dictionary with error details if invalid.
    """
    try:
        parsed = json.loads(output)

        if expected_structure:
            if expected_structure == "array" and not isinstance(parsed, list):
                return {
                    "valid": False,
                    "error_type": "JSONStructureError",
                    "message": "Expected a JSON array, but got a JSON object.",
                }
            elif expected_structure == "object" and not isinstance(parsed, dict):
                return {
                    "valid": False,
                    "error_type": "JSONStructureError",
                    "message": "Expected a JSON object, but got a JSON array.",
                }

        return True  # Valid JSON, and structure matches if specified

    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "error_type": "JSONDecodeError",
            "message": str(e),
            "line": e.lineno,
            "column": e.colno,
            "position": e.pos,
        }

def validate_html(output: str) -> Union[bool, Dict]:
    """
    Basic HTML validation.
    - If BeautifulSoup can parse at least one valid tag, we consider it 'valid enough'.
    - If no tags found or parse fails, we return invalid with fallback_ok=True
      so the system can still return a 200 OK with 'best effort' HTML.
    """
    from bs4 import BeautifulSoup  # Local import

    try:
        soup = BeautifulSoup(output, 'html.parser')

        if not soup.find():
            return {
                "valid": False,
                "error_type": "HTMLStructureError",
                "message": "No recognizable HTML tags found.",
                "fallback_ok": True,  # Allow 200 OK fallback
            }
        return True

    except Exception as e:
        return {
            "valid": False,
            "error_type": "HTMLParseError",
            "message": str(e),
            "fallback_ok": True,  # Allow 200 OK fallback
        }

def validate_python(output: str) -> Union[bool, Dict]:
    """
    Very basic Python code validation (checks for syntax errors).
    """
    try:
        compile(output, "<string>", "exec")
        return True
    except SyntaxError as e:
        return {
            "valid": False,
            "error_type": "PythonSyntaxError",
            "message": str(e),
            "line": e.lineno,
            "offset": e.offset,
        }
    except Exception as e:
        logger.error(f"Python code validation error (not syntax): {e}")
        return {
            "valid": False,
            "error_type": "PythonValidationError",
            "message": str(e),
        }

