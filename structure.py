# structure.py

import json
import logging
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StructureAnalyzer:
    """
    Standalone Structure Analyzer for input and output text.
    """

    def analyze_input_structure(self, input_text: str, content_type: str) -> Dict:
        """
        Analyzes the structure of user input text based on content type and heuristics.

        Args:
            input_text: The raw user input text.
            content_type: The Content-Type header of the input request.

        Returns:
            A dictionary containing the detected structure type, confidence, and metadata.
        """
        structure_info = {
            "input_structure_type": "unknown",
            "confidence": 0.1,  # Start with low confidence
            "features": {},
            "metadata": {},  # For additional, format-specific data
        }

        content_type_lower = content_type.lower()

        if content_type_lower == "application/json":
            try:
                parsed_json = json.loads(input_text)
                structure_info["input_structure_type"] = "json_input"
                structure_info["confidence"] = 0.95
                structure_info["features"]["is_valid_json"] = True
                if isinstance(parsed_json, dict):
                    structure_info["features"]["json_type"] = "object"
                elif isinstance(parsed_json, list):
                    structure_info["features"]["json_type"] = "array"

            except json.JSONDecodeError:
                structure_info["input_structure_type"] = "json_like_text_input"
                structure_info["confidence"] = 0.6  # Could be JSON-like, but not valid
                structure_info["features"]["is_valid_json"] = False

        elif content_type_lower == "text/csv":
            structure_info["input_structure_type"] = "csv_input"
            structure_info["confidence"] = 0.9
            # Basic CSV header and row detection
            lines = input_text.strip().splitlines()
            if lines:
                headers = [h.strip() for h in lines[0].split(',')]
                structure_info["metadata"]["csv_headers"] = headers
                structure_info["features"]["column_count"] = len(headers)
                structure_info["features"]["row_count"] = len(lines) - 1  # Excludes Header
                # Basic CSV validity check (consistent column count)
                if len(lines) > 1:
                    first_row_cols = len(lines[1].split(","))
                    if all(len(line.split(",")) == first_row_cols for line in lines[1:]):
                        structure_info["features"]["is_consistent_columns"] = True
                    else:
                        structure_info["features"]["is_consistent_columns"] = False

        elif content_type_lower == "application/x-www-form-urlencoded":
            structure_info["input_structure_type"] = "form_urlencoded_input"
            structure_info["confidence"] = 0.9
            # Basic key-value pair detection
            try:
                parsed_data = dict(re.findall(r'([^&=]+)=([^&]*)', input_text))  # Basic parsing
                structure_info["metadata"]["form_keys"] = list(parsed_data.keys())
                structure_info["features"]["key_value_pair_count"] = len(parsed_data)
            except:
                structure_info["confidence"] = 0.5  # Something went wrong in parsing

        elif content_type_lower.startswith("text/plain") or not content_type:
            structure_info["confidence"] = 0.7  # Reasonable Confidence
            if any(keyword in input_text.lower() for keyword in ["table", "tabular", "row", "column"]):
                structure_info["input_structure_type"] = "potentially_tabular_text_input"
            elif any(keyword in input_text.lower() for keyword in ["list", "item", "number", "bullet"]):
                structure_info["input_structure_type"] = "potentially_list_text_input"
            elif self._is_code_like(input_text):
                structure_info["input_structure_type"] = "code_like_text_input"
                structure_info["features"]["keywords"] = self._extract_code_keywords(input_text)
            else:
                structure_info["input_structure_type"] = "unstructured_text_input"

        elif content_type_lower == "application/xml" or content_type_lower == "text/xml":
            structure_info["input_structure_type"] = "xml_input"
            structure_info["confidence"] = 0.8
            try:
                soup = BeautifulSoup(input_text, "xml")
                structure_info["features"]["has_root_element"] = bool(soup.find())
                # Basic XML validity. Check for DTD or Schema in future if needed
            except Exception as e:
                structure_info["features"]["is_valid_xml"] = False
                structure_info["confidence"] = 0.4  # Parsing failure.
                logger.warning(f"XML parsing failed: {e}")

        else:
            structure_info["input_structure_type"] = "other_input_type"  # e.g., binary, custom

        logger.info(
            f"Input Structure Analysis: Type={structure_info['input_structure_type']}, "
            f"Confidence={structure_info['confidence']}, Metadata={structure_info['metadata']}"
        )
        return structure_info

    def analyze_output_structure(self, output_text: str, requested_format: str) -> dict:
        """
        Analyzes the structure of LLM output text.

        Args:
            output_text: The raw LLM output text.
            requested_format: The requested output format (e.g., "json", "html", "python", "plaintext").

        Returns:
            A dictionary containing the detected output structure type, confidence and metadata.
        """
        structure_info = {
            "output_structure_type": "unknown",
            "confidence": 0.1,  # Start with low confidence
            "features": {},
            "metadata": {},
        }
        requested_format_lower = requested_format.lower()

        # --- Additional Enhancement: sanitize text if the user requested JSON ---
        if requested_format_lower == "json":
            # Remove code fences, trailing '%', etc. before the official json.loads
            sanitized_text = self._sanitize_for_json(output_text)
            try:
                parsed_json = json.loads(sanitized_text)
                structure_info["output_structure_type"] = "valid_json_output"
                structure_info["confidence"] = 0.95
                structure_info["features"]["is_valid_json"] = True
                if isinstance(parsed_json, dict):
                    structure_info["features"]["json_type"] = "object"
                elif isinstance(parsed_json, list):
                    structure_info["features"]["json_type"] = "array"
            except json.JSONDecodeError:
                # If that fails, still fallback to _is_json_like check
                if self._is_json_like(sanitized_text):
                    structure_info["output_structure_type"] = "json_like_output"
                    structure_info["confidence"] = 0.6
                else:
                    structure_info["output_structure_type"] = "invalid_json_output"
                    structure_info["confidence"] = 0.2
                structure_info["features"]["is_valid_json"] = False

        elif requested_format_lower == "html":
            try:
                soup = BeautifulSoup(output_text, 'html.parser')
                if soup.find('table'):
                    structure_info["output_structure_type"] = "html_table_output"
                    structure_info["confidence"] = 0.9
                    table = soup.find('table')
                    headers = [th.text.strip() for th in table.find_all('th')] if table and table.find('th') else []
                    rows = table.find_all('tr')
                    row_count = len(rows) - 1 if headers else len(rows)  # exclude header row if exists
                    col_count = len(headers) if headers else (len(rows[0].find_all('td')) if rows and rows[0].find_all('td') else 0)

                    structure_info["metadata"]["html_table_headers"] = headers
                    structure_info["metadata"]["html_table_row_count"] = row_count
                    structure_info["metadata"]["html_table_col_count"] = col_count
                    structure_info["features"]["has_table"] = True

                elif soup.find('ul') or soup.find('ol'):
                    structure_info["output_structure_type"] = "html_list_output"
                    structure_info["confidence"] = 0.8
                    structure_info["features"]["has_list"] = True
                elif soup.find('p'):
                    structure_info["output_structure_type"] = "html_paragraph_output"
                    structure_info["confidence"] = 0.8
                    structure_info["features"]["has_paragraphs"] = True

                elif soup.find():  # Check for any HTML tag
                    structure_info["output_structure_type"] = "generic_html_output"
                    structure_info["confidence"] = 0.7
                else:  # No HTML tags found
                    structure_info["output_structure_type"] = "html_parsing_failed_output"
                    structure_info["confidence"] = 0.2

            except Exception as e:
                structure_info["output_structure_type"] = "html_parsing_failed_output"
                structure_info["confidence"] = 0.2
                logger.warning(f"HTML parsing failed: {e}")

        elif requested_format_lower == "python":
            if self._is_code_like(output_text):
                code_snippets = self._extract_python_code_heuristically(output_text)
                if code_snippets:
                    structure_info["output_structure_type"] = "python_code_output"
                    structure_info["confidence"] = 0.8
                    structure_info["metadata"]["python_code_snippet_count"] = len(code_snippets)
                    structure_info["features"]["keywords"] = self._extract_code_keywords(output_text)
            else:
                structure_info["output_structure_type"] = "no_python_code_output"
                structure_info["confidence"] = 0.2

        elif requested_format_lower == "plaintext":
            if re.match(r"^\s*[-*]\s", output_text, re.MULTILINE) or re.match(r"^\s*\d+\.\s", output_text, re.MULTILINE):
                structure_info["output_structure_type"] = "plaintext_list_output"
                structure_info["confidence"] = 0.7
            elif re.search(r"\|.*?\|.*?\|", output_text):
                structure_info["output_structure_type"] = "plaintext_table_like_output"
                structure_info["confidence"] = 0.6
            else:
                structure_info["output_structure_type"] = "plaintext_paragraph_output"
                structure_info["confidence"] = 0.8

        else:
            # Unknown or no requested format. Still try to analyze.
            # For JSON-like checks, sanitize first in case code fences or trailing '%' exist
            sanitized_text = self._sanitize_for_json(output_text)

            if self._is_json_like(sanitized_text):
                structure_info["output_structure_type"] = "json_like_output"
                structure_info["confidence"] = 0.6
            elif self._is_html_like(output_text):
                structure_info["output_structure_type"] = "html_like_output"
                structure_info["confidence"] = 0.6
            elif self._is_code_like(output_text):
                structure_info["output_structure_type"] = "code_like_output"
                structure_info["confidence"] = 0.6
            else:
                structure_info["output_structure_type"] = "unknown"
                structure_info["confidence"] = 0.1

        logger.info(
            f"Output Structure Analysis (Format: {requested_format}): "
            f"Type={structure_info['output_structure_type']}, "
            f"Confidence={structure_info['confidence']}, "
            f"Metadata={structure_info['metadata']}"
        )
        return structure_info

    def _sanitize_for_json(self, text: str) -> str:
        """
        Removes code fences (```json ... ```), trailing '%', and extra whitespace
        from text that is supposed to be (or might be) JSON. This helps prevent
        false 'invalid_json_output' classifications when the LLM returns 
        markdown fences or terminal artifacts.
        """
        # Remove any ```json (or ``` with/without the word 'json') fences
        text_no_fences = re.sub(r"(?s)```(?:json|JSON)?\s*(.*?)```", r"\1", text.strip())

        # Remove a single trailing '%' if present (e.g., shell artifact)
        if text_no_fences.endswith('%'):
            text_no_fences = text_no_fences[:-1]

        # Finally, strip extra whitespace
        return text_no_fences.strip()

    def _extract_python_code_heuristically(self, text: str) -> list[str]:
        """
        Heuristic Python code extraction (similar to output_parser.py, 
        simplified for standalone script).
        """
        code_snippets = []
        backtick_code_regex = re.compile(r"```(?:python)?\s*([\s\S]*?)```", re.MULTILINE)
        backtick_matches = backtick_code_regex.findall(text)
        code_snippets.extend(backtick_matches)

        # Regex for indented code blocks (4 spaces) - Simple heuristic, can be improved
        indented_code_regex = re.compile(r"^( {4,}|\t+)(.*)$", re.MULTILINE)
        indented_matches = indented_code_regex.findall(text)

        if not code_snippets and indented_matches:  # Basic indented code extraction
            current_block = ""
            for indent, code_line in indented_matches:
                if not current_block and code_line.strip():  # Start new block
                    current_block += code_line.strip() + "\n"
                elif current_block and code_line.strip():  # Continue block
                    current_block += code_line.strip() + "\n"
                elif current_block:  # End of block (heuristic)
                    code_snippets.append(current_block.strip())
                    current_block = ""
                if current_block.strip():
                    code_snippets.append(current_block.strip())

        return [snippet.strip() for snippet in code_snippets if snippet.strip()]

    def _is_json_like(self, text: str) -> bool:
        """
        Checks for basic JSON-like characteristics (more robust).
        First, we call _sanitize_for_json() to remove code fences,
        trailing '%', etc.
        """
        # Sanitize first
        text = self._sanitize_for_json(text)

        # Then do bracket matching
        if (text.startswith("{") and text.endswith("}")) or (text.startswith("[") and text.endswith("]")):
            stack = []
            for char in text:
                if char in ['{', '[']:
                    stack.append(char)
                elif char in ['}', ']']:
                    if not stack:
                        return False  # Unmatched closing bracket
                    opening = stack.pop()
                    if (char == '}' and opening != '{') or (char == ']' and opening != '['):
                        return False  # Mismatched brackets
            return not stack  # True if stack is empty (all brackets matched)
        return False

    def _is_code_like(self, text: str) -> bool:
        """
        Checks for very basic code-like characteristics (keywords, indentation).
        """
        keywords = ["def", "import", "class", "if", "else", "for", "while", "return", "print", "try", "except", "finally"]
        # Regex for code-like indentation (spaces or tabs at the beginning of a line)
        indentation_regex = re.compile(r"^( {2,}|\t+)", re.MULTILINE)
        if any(keyword in text for keyword in keywords) or indentation_regex.search(text):
            return True

        return False

    def _extract_code_keywords(self, text: str) -> List[str]:
        """
        Extract potential code keywords.
        """
        keywords = ["def", "import", "class", "if", "else", "for", "while", "return", "print", "try", "except", "finally"]
        found_keywords = [keyword for keyword in keywords if keyword in text]
        return found_keywords

    def _is_html_like(self, text: str) -> bool:
        """
        Checks for basic HTML-like characteristics (tags).
        """
        text_lower = text.lower()
        if "<html" in text_lower or "<body" in text_lower or "<div" in text_lower or "<table" in text_lower or "<p" in text_lower:
            return True
        return False

    def learn_from_interaction(self, input_structure: Dict, output_structure: Dict, validation_result: Union[Dict, bool], context: Dict):
        """
        Learns from interaction data. (Placeholder)
        """
        logger.info(
            f"Learning from interaction: Input Structure: {input_structure}, "
            f"Output Structure: {output_structure}, "
            f"Validation Result: {validation_result}, "
            f"Context: {context}"
        )
        # Basic Learning Logic (adjust confidence based on validation)
        if isinstance(validation_result, bool):
            if validation_result:  # Success
                input_structure["confidence"] = min(1.0, input_structure["confidence"] + 0.1)
                output_structure["confidence"] = min(1.0, output_structure["confidence"] + 0.1)
            else:  # Failure
                input_structure["confidence"] = max(0.0, input_structure["confidence"] - 0.1)
                output_structure["confidence"] = max(0.0, output_structure["confidence"] - 0.1)
        elif isinstance(validation_result, dict) and "valid" in validation_result:  # Detailed validation report
            if validation_result["valid"]:  # Success
                input_structure["confidence"] = min(1.0, input_structure["confidence"] + 0.1)
                output_structure["confidence"] = min(1.0, output_structure["confidence"] + 0.1)
            else:  # Failure
                input_structure["confidence"] = max(0.0, input_structure["confidence"] - 0.1)
                output_structure["confidence"] = max(0.0, output_structure["confidence"] - 0.1)
        # More advanced learning (adjust based on error type, features etc.) would go here.

if __name__ == "__main__":
    analyzer = StructureAnalyzer()

    print("--- Input Structure Analysis Examples ---")
    input_examples = [
        ("What is the capital of France?", "text/plain"),
        ('{"question": "List 5 largest cities", "output_format": "json"}', "application/json"),
        ("Name,Age,City\nAlice,30,NY\nBob,25,London", "text/csv"),
        ("<request><question>Benefits of XML?</question></request>", "application/xml"),
        ("Give me a table of planets", "text/plain"),  # Potentially tabular input
        ('{"bad json}', "application/json"),  # Invalid JSON
        ("question=What+is+your+name?&output_format=html", "application/x-www-form-urlencoded"),
        ("", "text/plain"),  # Empty input
        ("  def my_func():\n    pass", "text/plain"),  # Indented code
        ("This is a list:\n- item 1\n- item 2", "text/plain"),  # Plaintext List
    ]
    for text, content_type in input_examples:
        print(f"\nInput: Content-Type='{content_type}', Text='{text[:50]}...'")
        input_structure = analyzer.analyze_input_structure(text, content_type)
        print(f"Detected Input Structure: {input_structure}")

    print("\n--- Output Structure Analysis Examples ---")
    output_examples = [
        ('{"answer": "Paris"}', "json"),
        ('```json\n{"city": "London", "population": 9000000}\n```', "json"),  # JSON in Markdown fences
        ('<table><tr><th>City</th><th>Population</th></tr><tr><td>London</td><td>9M</td></tr></table>', "html"),
        ("<p>This is a paragraph of text.</p>", "html"),
        ("def add(a, b):\n  return a + b", "python"),
        ("Here are the capitals:\n1. Paris\n2. London", "plaintext"),
        ("Color | Hex Code\n------|---------\nRed   | #FF0000", "plaintext"),  # Table-like plaintext
        ('{}', "json"),  # Empty JSON object
        ('<bad-html', "html"),  # Invalid HTML
    ]
    for text, format in output_examples:
        print(f"\nOutput (Format='{format}'): Text='{text[:50]}...'")
        output_structure = analyzer.analyze_output_structure(text, format)
        print(f"Detected Output Structure: {output_structure}")
