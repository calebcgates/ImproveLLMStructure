
# output_parser.py
import json
import logging
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

from data_structures import universal_representation
from structure import StructureAnalyzer

logger = logging.getLogger(__name__)

def parse_llm_output(raw_llm_response: str, requested_format: str, context: dict) -> dict:
    """
    Parses the raw LLM response string, guided by structure analysis and with robust cleanup.
    Ensures final universal_representation has a valid data structure for the user’s requested format
    (e.g. valid JSON, minimal HTML, Python code snippet, or plain text).
    Prioritizes requested_format and considers output_intent.
    """

    # 1) Clean up disclaimers, code fences, etc. regardless of format
    cleaned_response = _cleanup_common_artifacts(raw_llm_response)

    # 2) Prepare the universal representation
    parsed_output = universal_representation.copy()

    # 3) Parse logic depends on the user’s requested format:
    if requested_format.lower() == "json":
        _parse_as_json(cleaned_response, parsed_output, context)  # Pass context

    elif requested_format.lower() == "html":
        _parse_as_html(cleaned_response, parsed_output, context)

    elif requested_format.lower() == "python":
        _parse_as_python(cleaned_response, parsed_output, context)  # Pass context

    elif requested_format.lower() == "plaintext":
        # Always accept as is
        parsed_output["text_content"] = cleaned_response

    else:
        # Unknown or custom format => fallback to plaintext
        logger.warning(f"Unknown requested format '{requested_format}'. Using plaintext fallback.")
        parsed_output["text_content"] = cleaned_response

    # --- Structure Analysis (AFTER Format-Specific Parsing) ---
    structure_analyzer = StructureAnalyzer()
    output_structure = structure_analyzer.analyze_output_structure(cleaned_response, requested_format)
    parsed_output["output_structure"] = output_structure  # Store it

    logger.debug(f"Final Parsed Output: {parsed_output}")
    return parsed_output

# ------------------------------------------------------------------------
#                        PARSE FOR SPECIFIC FORMATS
# ------------------------------------------------------------------------

def _parse_as_json(cleaned_response: str, parsed_output: dict, context: dict) -> None:
    """
    Attempt to parse the LLM response as JSON.
    Handles object vs. array discrepancies and sets an error flag if needed.
    """
    extracted_json = _extract_and_parse_json(cleaned_response)
    if extracted_json is not None:
        if isinstance(extracted_json, list) and ("array" in context["prompt_text"].lower() or (isinstance(context.get("input_structure"), dict) and context.get("input_structure",{}).get("input_structure_type") == "json_input" and context["input_structure"].get("features", {}).get("json_type") == "array")):
            parsed_output["json_fields"] = extracted_json
            return
        elif isinstance(extracted_json, dict) and ("array" not in context["prompt_text"].lower() or (isinstance(context.get("input_structure"), dict) and context.get("input_structure", {}).get("input_structure_type") == "json_input" and context["input_structure"].get("features",{}).get("json_type") == "object")):
            parsed_output["json_fields"] = extracted_json
            return
        else:
            # WRONG STRUCTURE! Trigger error correction.
            logger.warning("Incorrect JSON structure (object vs. array).")
            parsed_output["json_fields"] = extracted_json  # Store what we have
            parsed_output["error"] = "IncorrectJSONStructure"  # Set an error flag
            return

    # --- Fallback (if no valid JSON could be extracted) ---
    try:
        fallback_json = json.loads(cleaned_response)
        parsed_output["json_fields"] = fallback_json
    except Exception as e:
        logger.warning(f"Could not parse as JSON: {e}")
        parsed_output["json_fields"] = {
            "error": "Could not parse JSON",
            "raw_text": cleaned_response[:500],  # Store a snippet
        }

def _parse_as_html(cleaned_response: str, parsed_output: dict, context: dict) -> None:
    """
    Attempt to parse LLM response as HTML.
    If it fails or no tags found, forcibly produce minimal HTML skeleton.
    """
    # If structure indicates 'html_table_output' or 'html_like_output', let's try to parse
    try:
        soup = BeautifulSoup(cleaned_response, 'html.parser')
        # Check if we found any real HTML tags
        if soup.find():
            # Looks valid enough
            parsed_output["html_content"] = str(soup)
            return
        else:
            # fallback
            logger.warning("HTML parse found no tags. Forcing minimal HTML.")
            parsed_output["html_content"] = _minimal_html(cleaned_response)
    except Exception as e:
        logger.warning(f"HTML parse error, forcing minimal HTML: {e}")
        parsed_output["html_content"] = _minimal_html(cleaned_response)

def _parse_as_python(cleaned_response: str, parsed_output: dict, context: dict) -> None:
    """
    Attempt to extract Python code from LLM response, considering output_intent.
    If none found and intent is code_only, forcibly produce minimal code snippet.
    """
    code_snippets = _extract_python_code(cleaned_response)

    if context["output_intent"] == "code_only":
        if code_snippets:
            parsed_output["code_snippets"] = code_snippets
        else:
            logger.warning("No valid Python snippet found (code_only intent).")
            parsed_output["code_snippets"] = [] # Return Empty List
            parsed_output["error"] = "NoCodeFound"
    elif context["output_intent"] == "code_with_explanation":
        # Keep everything
        parsed_output["code_snippets"] = code_snippets
        parsed_output["text_content"] = cleaned_response

# ------------------------------------------------------------------------
#                 HELPER FUNCTIONS FOR MINIMAL FALLBACKS
# ------------------------------------------------------------------------

def _minimal_html(original_text: str) -> str:
    """
    Produce a minimal HTML skeleton if we can't parse actual HTML.
    We include the original text inside a <p> as fallback.
    """
    sanitized = _remove_triple_backticks(original_text)
    sanitized = sanitized.replace("<", "<").replace(">", ">")  # Escape
    return f"<html><body><p>{sanitized}</p></body></html>"

def _minimal_python(original_text: str) -> str:
    """
    Produce minimal Python code snippet, embedding the raw text as a comment.
    """
    placeholder = (
        "# Could not parse Python from the LLM response.\n"
        "# Original snippet:\n"
        "# " + original_text.replace("\n", "\n# ")[:500] + "\n\n"
        "def placeholder_function():\n"
        "    pass\n"
    )
    return placeholder

# ------------------------------------------------------------------------
#                 GENERAL CLEANUP & JSON EXTRACTION LOGIC
# ------------------------------------------------------------------------

def _cleanup_common_artifacts(text: str) -> str:
    """
    Removes disclaimers, code fences, 'result' key, etc.
    This step can be adapted to your LLM's typical style.
    """
    # Remove triple backticks
    text = re.sub(r"```(?:\w+)?\s*", "", text)
    text = text.replace("```", "")

    # Remove leading "result": wrapper if it exists
    # e.g. {"result":  ... }
    text = re.sub(r'^\{"result":\s*(.+)\}\s*$', r'\1', text.strip(), flags=re.DOTALL)

    # Example disclaimers or repeated phrases to remove
    disclaimers = [
        r"As an AI language model,? (I )?(can('?t)?|am\sable\s(to)?)",
        r"I am an AI model",
        r"I'm just an AI model",
    ]
    for pattern in disclaimers:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text.strip()

def _extract_and_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Attempt to robustly parse JSON from text.
    If no valid JSON found, returns None.
    """
    # A quick pass to remove leftover "```json" or "```"
    text = re.sub(r"```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "")

    # Try bracket-based search
    return extract_json_robust(text)

def extract_json_robust(text: str) -> Optional[Dict[str, Any]]:
    """
    Tries to find the first valid JSON object or array in the text
    by scanning for balanced braces/brackets.
    Returns None if none found.
    """
    # 1. Look for first balanced { ... }
    stack = []
    start_index = -1
    for i, char in enumerate(text):
        if char == '{':
            if not stack:
                start_index = i
            stack.append(char)
        elif char == '}':
            if stack and stack[-1] == '{':
                stack.pop()
                if not stack:
                    json_str = text[start_index:i + 1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        # keep looking
                        continue
            else:
                # mismatch, reset
                stack = []
                start_index = -1

    # 2. If no object found, look for first balanced [ ... ]
    stack = []
    start_index = -1
    for i, char in enumerate(text):
        if char == '[':
            if not stack:
                start_index = i
            stack.append(char)
        elif char == ']':
            if stack and stack[-1] == '[':
                stack.pop()
                if not stack:
                    json_str = text[start_index:i + 1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        continue
            else:
                stack = []
                start_index = -1

    # No valid JSON found
    return None

def _extract_python_code(text: str) -> list[str]:
    """
    Extracts Python code snippets from text using code fences or
    4-space/tabs indentation as heuristics.
    """
    code_snippets = []

    # Code fence approach
    fence_regex = re.compile(r"```(?:python)?\s*([\s\S]*?)```", re.MULTILINE)
    matches = fence_regex.findall(text)
    code_snippets.extend(matches)

    # Indented code blocks
    indented_code_regex = re.compile(r"^( {4,}|\t+)(.*)$", re.MULTILINE)
    indented_matches = indented_code_regex.findall(text)

    if not code_snippets and indented_matches:
        current_block = ""
        for indent, code_line in indented_matches:
            if not current_block and code_line.strip():
                current_block += code_line.strip() + "\n"
            elif current_block and code_line.strip():
                current_block += code_line.strip() + "\n"
            else:
                # end of block
                if current_block.strip():
                    code_snippets.append(current_block.strip())
                current_block = ""
        # in case there's trailing block
        if current_block.strip():
            code_snippets.append(current_block.strip())

    # Clean up leading/trailing whitespace
    return [c.strip() for c in code_snippets if c.strip()]

def _remove_triple_backticks(text: str) -> str:
    """
    Removes any triple backticks from text (```...```),
    ignoring language hints.
    """
    return re.sub(r"```(?:\w+)?\s*", "", text).replace("```", "")

