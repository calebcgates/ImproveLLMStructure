# error_corrector.py 

import json
import logging
from typing import Optional, Dict, Union

from llm_manager import send_prompt_to_llm
from format_transformer import get_transformer
from output_parser import parse_llm_output, _extract_and_parse_json
from validator import validate_output
from config import ERROR_CORRECTION_RETRIES

logger = logging.getLogger(__name__)

async def correct_output(universal_representation: dict, requested_format: str, raw_llm_response: str, context: dict, validation_result: Union[bool, Dict]) -> str:
    """
    Attempts to correct errors in the transformed output using heuristic correction
    and iterative prompting with the LLM, guided by validation reports. Considers
    output_intent and uses targeted prompts.
    """
    transformed_output = ""

    # --- Heuristic Correction ---
    heuristic_corrected_representation = _heuristic_correction(universal_representation, requested_format)
    if heuristic_corrected_representation:
        transformer = get_transformer(requested_format)
        transformed_output = transformer.transform(heuristic_corrected_representation, context) # Pass context
        validation_after_heuristic = validate_output(transformed_output, requested_format)  # No expected_structure yet
        if isinstance(validation_after_heuristic, bool) and validation_after_heuristic is True:
            logger.info("Heuristic correction successful.")
            return transformed_output
        elif isinstance(validation_after_heuristic, dict) and validation_after_heuristic["valid"] is True:
            logger.info("Heuristic correction successful (with report).")
            return transformed_output
        else:
            logger.warning("Heuristic correction did not fully validate, proceeding to iterative prompting.")
            validation_result = validation_after_heuristic # Use the result from the validator

    # --- Iterative Prompting ---
    last_error = "Initial Validation Failed"
    if isinstance(validation_result, dict) and "message" in validation_result:
        last_error = validation_result["message"]

    expected_structure = None
    if requested_format == "json" and "prompt_text" in context:
        if "array" in context["prompt_text"].lower():
            expected_structure = "array"
        elif "object" in context["prompt_text"].lower():
            expected_structure = "object"

    current_representation = universal_representation  # Start with current
    for attempt in range(ERROR_CORRECTION_RETRIES):
        logger.info(f"Iterative correction attempt: {attempt + 1}/{ERROR_CORRECTION_RETRIES}")

        prompt = None
        if isinstance(validation_result, dict) and "error_type" in validation_result:
            error_type = validation_result["error_type"]

            # --- Format-Specific Correction Prompts ---
            if requested_format == "json":
                if error_type == "JSONDecodeError":
                    prompt = _construct_json_correction_prompt(validation_result, raw_llm_response)
                elif error_type == "JSONStructureError":
                    prompt = _construct_json_structure_prompt(validation_result, raw_llm_response, context)
                # Add other JSON-specific error types if needed
            elif requested_format == "html":
                if error_type in ["HTMLStructureError", "HTMLParseError"]:
                    prompt = _construct_html_correction_prompt(validation_result, raw_llm_response)
            elif requested_format == "python":
                if error_type in ["PythonSyntaxError", "PythonValidationError"]:
                    prompt = _construct_python_correction_prompt(validation_result, raw_llm_response)

        # --- General Format Correction (if no specific prompt was created) ---
        if prompt is None:
             prompt = _construct_format_correction_prompt(raw_llm_response, requested_format, last_error, validation_result)

        if context.get("output_intent") == "code_only":
            prompt += " Return only the code, with no additional text"

        logger.debug(f"Correction prompt: {prompt}")
        corrected_response = await send_prompt_to_llm(prompt)

        if corrected_response.startswith("Error:"):
            logger.warning(f"LLM call failed: {corrected_response}")
            break

        # --- Parse and Re-validate (Crucial!) ---
        corrected_representation = parse_llm_output(corrected_response, requested_format, context) # Pass context
        transformer = get_transformer(requested_format)
        transformed_output = transformer.transform(corrected_representation, context) # Pass context
        validation_result = validate_output(transformed_output, requested_format, expected_structure)

        if isinstance(validation_result, (bool, dict)) and (validation_result is True or (isinstance(validation_result, dict) and validation_result.get("valid", False))):
            logger.info(f"Correction successful after {attempt + 1} attempts.")
            return transformed_output

        else:
            last_error = "Iterative Correction Failed Validation"  # Generic
            if isinstance(validation_result, dict) and "message" in validation_result:
                last_error = validation_result["message"]  # Use message
            logger.warning(f"Correction attempt {attempt + 1} failed. Error: {last_error}")

    logger.warning("Iterative correction failed after multiple attempts.")
    return transformed_output  # Return best attempt

# --- Helper Functions (Targeted Correction Prompts) ---
def _construct_json_structure_prompt(validation_result: Union[bool, Dict], raw_llm_response: str, context: dict) -> str:
    """Constructs a prompt for correcting JSON array/object structure."""
    if isinstance(validation_result, dict) and "message" in validation_result:
        message = validation_result["message"]
        if "Expected a JSON array" in message:
            return (
                f"The previous response was intended to be a JSON array, but it was a JSON object. "
                f"Please provide the response as a valid JSON *array*, according to the original request. "
                f"Original request: {context.get('prompt_text', '')} "
                f"Previous response: {raw_llm_response}"
            )
        elif "Expected a JSON object" in message:
            return (
                f"The previous response was intended to be a JSON object, but it was a JSON array. "
                f"Please provide the response as a valid JSON *object*, according to the original request. "
                f"Original request: {context.get('prompt_text', '')} "
                f"Previous response: {raw_llm_response}"
            )
    return ( # Fallback
        f"The previous response was intended to be JSON, but its structure was incorrect (array vs. object). "
        f"Please provide valid JSON with the correct structure, based on the original request. "
        f"Original request: {context.get('prompt_text', '')} "
        f"Previous response: {raw_llm_response}"
    )

def _construct_json_correction_prompt(validation_result: Union[bool, Dict], raw_llm_response: str) -> str:
    """Constructs a JSON-specific correction prompt."""
    if isinstance(validation_result, dict) and "error_type" in validation_result:
        if validation_result["error_type"] == "JSONDecodeError":
            message = validation_result.get("message", "Invalid JSON")
            line = validation_result.get("line")
            column = validation_result.get("column")
            return (
                f"The previous response was intended to be JSON, but it contains a syntax error: {message} (line {line}, column {column}). "
                f"Please provide valid JSON.  Do not include any surrounding text or explanations. Return ONLY the JSON data. "
                f"Previous response: {raw_llm_response}"
            )
    return (
        f"The previous response was intended to be JSON, but it's invalid. "
        f"Please provide valid JSON. Do not include any surrounding text or explanations. Return ONLY the JSON data. "
        f"Previous response: {raw_llm_response}"
    )

def _construct_html_correction_prompt(validation_result: Union[bool, Dict], raw_llm_response: str) -> str:
    """Constructs an HTML-specific correction prompt."""
    if isinstance(validation_result, dict) and "error_type" in validation_result:
        if validation_result["error_type"] == "HTMLStructureError":
            message = validation_result.get("message", "Invalid HTML")
            return (
                f"The previous response was intended to be HTML, but its structure is invalid: {message}. "
                f"Please provide valid HTML, paying close attention to proper tag nesting and closing tags. "
                f"Previous response: {raw_llm_response}"
            )
    return (
        f"The previous response was intended to be HTML, but it's invalid. "
        f"Please provide valid HTML. "
        f"Previous response: {raw_llm_response}"
    )

def _construct_python_correction_prompt(validation_result: Union[bool, Dict], raw_llm_response: str) -> str:
    """Constructs a Python-specific correction prompt."""
    if isinstance(validation_result, dict) and "error_type" in validation_result:
        if validation_result["error_type"] == "PythonSyntaxError":
            message = validation_result.get("message", "Invalid Python")
            line = validation_result.get("line")
            offset = validation_result.get("offset")
            return (
                f"The previous response was intended to be Python code, but it contains a syntax error: {message} (line {line}, offset {offset}). "
                f"Please provide valid Python code. "
                f"Previous response: {raw_llm_response}"
            )
    return (
        f"The previous response was intended to be Python code, but it's invalid. "
        f"Please provide valid Python code. "
        f"Previous response: {raw_llm_response}"
    )

def _construct_format_correction_prompt(raw_llm_response: str, requested_format: str, last_error_message: str, validation_result: Union[bool, Dict]) -> str:
    """
    Constructs a prompt to ask the LLM to correct the output format.
    """
    error_detail = ""
    if isinstance(validation_result, dict):
        error_type = validation_result.get("error_type", "FormatValidationError")
        error_message_detail = validation_result.get("message", last_error_message)
        error_detail = f" The previous response had a {error_type}: {error_message_detail}."
    else:
        error_detail = f" The previous response was invalid for the {requested_format} format."

    return (
        f"The previous response was supposed to be in {requested_format} format, but it was invalid."
        f"{error_detail} "
        f"Please reformat your previous response to be valid {requested_format}. "
        f"Ensure the response is ONLY in {requested_format} without any extra text or explanations. "
        f"Previous response: {raw_llm_response}"
    )

def _heuristic_correction(universal_representation: dict, requested_format: str) -> Optional[dict]:
    """Applies heuristic-based correction to the universal representation."""
    if requested_format == "json":
        if universal_representation["text_content"]:
            text_content = universal_representation["text_content"].strip()
            if text_content.startswith("{") and text_content.endswith("}"):
                try:
                    corrected_json = json.loads(text_content)
                    corrected_representation = universal_representation.copy()
                    corrected_representation["json_fields"] = corrected_json
                    corrected_representation["text_content"] = None  # Clear text
                    logger.info("Heuristic JSON correction applied (from text).")
                    return corrected_representation
                except json.JSONDecodeError:
                    logger.debug("Heuristic JSON correction failed.")
                    return None
    return None
