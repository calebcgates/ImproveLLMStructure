# prompt_handler.py

import json
import logging
import re
import urllib.parse
from typing import Optional, Dict

from llm_manager import send_prompt_to_llm
from config import DEFAULT_OUTPUT_FORMAT, LANGUAGE_CONFIG
from structure import StructureAnalyzer

logger = logging.getLogger(__name__)

async def handle_user_request(request_headers: dict, request_body: bytes) -> dict:
    """
    Asynchronously handles user requests, parses input, deduces output format & intent,
    constructs prompts, and manages context.
    """
    context = {
        "raw_input_data": request_body.decode('utf-8', errors='ignore'),
        "input_format_type": None,
        "prompt_text": None,
        "requested_format": None,
        "instructions": [],
        "simplified_prompt": None,
        "llm_format_deduction_response": None,
        "input_structure": None,
        "output_intent": "code_with_explanation",  # Default intent
        "error": None
    }

    content_type = request_headers.get("content-type", "text/plain").lower()  # Default and lowercase
    context["input_format_type"] = content_type
    logger.debug(f"Content-Type: {content_type}")

    structure_analyzer = StructureAnalyzer()
    context["input_structure"] = input_structure = structure_analyzer.analyze_input_structure(context["raw_input_data"], content_type)
    logger.debug(f"Input Structure Analysis: {input_structure}")

    # --- Input Parsing ---
    try:
        if content_type == "application/json":
            try:
                input_data = json.loads(context["raw_input_data"])
                logger.debug(f"Parsed JSON input: {input_data}")
                context["prompt_text"] = input_data.get("question") # Ensure we have prompt_text
                # Explicitly get and lowercase the requested format.
                context["requested_format"] = input_data.get("output_format", "").lower()
                intent = input_data.get("intent")
                logger.debug(f"Requested Format (from JSON): {context['requested_format']}") # Log after getting it
            except json.JSONDecodeError as e:
                context["prompt_text"] = context["raw_input_data"]
                context["error"] = f"Invalid JSON: {str(e)}"
                logger.warning(f"JSON Decode Error, treating input as plaintext: {e}")
                return context

            if context["prompt_text"] is None:
                context["error"] = "Missing question in JSON request"
                logger.warning("JSON input missing 'question' key")
                return context

        elif content_type == "application/x-www-form-urlencoded":
            try:
                parsed_body = urllib.parse.parse_qs(context["raw_input_data"])
                logger.debug(f"Parsed form data: {parsed_body}")
                context["prompt_text"] = parsed_body.get("question", [""])[0]
                # Explicitly get and lowercase the requested format.
                context["requested_format"] = parsed_body.get("output_format", [""])[0].lower()
                intent = parsed_body.get("intent", [""])[0]
                logger.debug(f"Requested Format (from form): {context['requested_format']}") # Log after getting
            except Exception as e:
                context["prompt_text"] = context["raw_input_data"]
                context["error"] = f"Error parsing form data: {str(e)}"
                logger.exception(f"Error parsing form data: {e}")  # Use logger.exception
                return context

        elif content_type.startswith("text/plain"):
            logger.debug("Treating input as plaintext")
            context["prompt_text"] = context["raw_input_data"]
            intent = None

        elif content_type == "text/csv":
            # CSV Handling (keep your existing logic here)
            if context["input_structure"]["input_structure_type"] == "csv_input":
                logger.debug("Confirmed CSV input structure")
                context["prompt_text"] = context["raw_input_data"]
                context["requested_format"] = "json"  # Default to JSON for CSV
                context["simplified_prompt"] = (
                    "Convert the following CSV data to JSON: " + context["raw_input_data"]
                )
                intent = None
            else:
                context["prompt_text"] = context["raw_input_data"]
                logger.warning("Content-Type was text/csv, but structure analysis did not confirm CSV format.")
                intent = None  # Intent needs to be deduced

        elif content_type in ("application/xml", "text/xml", "application/octet-stream"):
            logger.debug(f"Content-Type {content_type} - treating as plaintext")
            context["prompt_text"] = context["raw_input_data"]  # Use as plain text
        #elif content_type == "application/octet-stream": # Handled with in statment above
          #  context["prompt_text"] = ""
          #  context["error"] = "Unsupported content type: application/octet-stream"
          #  return context
        else:
            logger.info(f"Unknown Content-Type: {content_type}. Treating as plaintext.")
            context["prompt_text"] = context["raw_input_data"]
            intent = None

    except Exception as e: # More general exception
        logger.exception(f"Error parsing input: {e}")
        context["error"] = "Error parsing request"
        return context # Exit the handler



    # --- Explicit Intent Parameter Handling ---
    if intent:
        intent = intent.lower().replace("_", "").replace(" ", "")
        if intent in ["codeonly", "justcode", "executablecode"]:
            context["output_intent"] = "code_only"
        elif intent in ["codewithexplanation", "explaincode", "withcomments", "documented"]:
            context["output_intent"] = "code_with_explanation"
        else:
            logger.warning(f"Unknown intent value: {intent}. Using default.")
            # context["output_intent"] remains the default

    # --- Intent and Format Deduction ---
    # 1. Agent Prompt Analysis (PRIORITY)
    if not intent or not context["requested_format"]:
        deduced_format, deduced_intent = _analyze_for_agent_prompt(context["prompt_text"])
        logger.debug(f"Agent Prompt Analysis - Format: {deduced_format}, Intent: {deduced_intent}")
        if deduced_format:
            context["requested_format"] = deduced_format
            logger.debug(f"Format set by agent analysis: {deduced_format}")
        if deduced_intent:
            context["output_intent"] = deduced_intent
            logger.debug(f"Intent set by agent analysis: {deduced_intent}")


    # 2. Intent Deduction (if not explicitly provided and not from agent)
    if not context["output_intent"]:  # Use context, not the local variable
        prompt_text_lower = context["prompt_text"].lower() if context["prompt_text"] else ""
        logger.debug("No explicit intent or agent intent found. Deduce intent from keywords.")
        if context["requested_format"] in ["python", "plaintext"] or any(keyword in prompt_text_lower for keyword in LANGUAGE_CONFIG.get("python",{}).get("keywords",[])):  # Check Python keywords
            if any(keyword in prompt_text_lower for keyword in ["onlycode", "justcode", "executablecode", "nocomments", "noexplanation"]):
                context["output_intent"] = "code_only"
                logger.debug("Intent deduced: code_only (keywords)")
            elif any(keyword in prompt_text_lower for keyword in ["explain", "explanation", "comments", "howitworks", "withcomments", "documented"]):
                context["output_intent"] = "code_with_explanation"
                logger.debug("Intent deduced: code_with_explanation (keywords)")
            elif "how" in prompt_text_lower.split():
                context["output_intent"] = "code_with_explanation"
                logger.debug("Intent deduced: code_with_explanation ('how' keyword)")



    # 3. Format Deduction (if not explicitly provided and not from agent)
    if not context["requested_format"]:
        logger.debug("No explicit format or agent format found. Deduce format from heuristics/LLM.")
        prompt_text_lower = context["prompt_text"].lower() if context["prompt_text"] else ""

        # --- Heuristics ---
        if context["input_structure"]["input_structure_type"] == "json_input" and context["input_structure"]["confidence"] > 0.8:
            context["requested_format"] = "json"
            logger.debug("Format deduced: json (JSON input structure)")
        elif context["input_structure"]["input_structure_type"] == "csv_input" and context["input_structure"]["confidence"] > 0.8:
            context["requested_format"] = "json"
            logger.debug("Format deduced: json (CSV input structure)")
        elif "json" in prompt_text_lower or content_type == "application/json":
            context["requested_format"] = "json"
            logger.debug("Format deduced: json (keywords or content type)")
        elif "html" in prompt_text_lower or "table" in prompt_text_lower:
            context["requested_format"] = "html"
            logger.debug("Format deduced: html (keywords)")
        elif "python" in prompt_text_lower or "code" in prompt_text_lower:
            context["requested_format"] = "python"
            logger.debug("Format deduced: python (keywords)")
        else:
            logger.debug("No format deduced from heuristics. Trying LLM format deduction.")
            # --- LLM-Assisted Format Deduction ---
            if context["input_structure"]["confidence"] < 0.6:  # Only use LLM if heuristics are unsure
                format_deduction_prompt = (
                    "Based on the following user request, rank the output formats in order of likelihood (most likely first): "
                    "JSON, HTML, Python, PlainText. Provide only the ranked list of formats, comma-separated. "
                    f"Request: {context['prompt_text']}"
                )
                logger.info(f"Sending format deduction prompt to LLM: {format_deduction_prompt}")
                llm_format_response = await send_prompt_to_llm(format_deduction_prompt)
                context["llm_format_deduction_response"] = llm_format_response
                logger.info(f"LLM format deduction response: {llm_format_response}")

                if llm_format_response and not llm_format_response.startswith("Error:"):
                    ranked_formats = [f.strip().lower() for f in llm_format_response.split(",") if f.strip()]
                    for fmt in ranked_formats:
                        if fmt in ["json", "html", "python", "plaintext"]:  # Use explicit list
                            context["requested_format"] = fmt
                            logger.debug(f"Format deduced by LLM: {fmt}")
                            break
            else:
                logger.debug(f"Skipping LLM format deduction (high confidence or format already deduced): {context['input_structure']}")

        # --- Default Fallback ---
        if not context["requested_format"]:
            context["requested_format"] = DEFAULT_OUTPUT_FORMAT.lower()
            logger.debug(f"Format defaulted to: {DEFAULT_OUTPUT_FORMAT.lower()}")

    logger.debug(f"Final requested_format: {context['requested_format']}")  # Log the FINAL requested_format
    logger.debug(f"Final output_intent: {context['output_intent']}") # Log the FINAL

    # --- Prompt Construction ---
    input_structure_info = ""
    if context["input_structure"]["input_structure_type"] == "json_input":
        input_structure_info = "The user provided the following JSON data: "
    elif context["input_structure"]["input_structure_type"] == "csv_input":
        input_structure_info = "The user provided the following CSV data: "
    elif context["input_structure"]["input_structure_type"] == "form_urlencoded_input":
        input_structure_info = "The user provided the following form data: "
    elif context["input_structure"]["input_structure_type"] == "xml_input":
        input_structure_info = "The user provided the following XML data: "

    # Construct prompt based on requested format and intent
    if context["requested_format"] == "json":
        context["simplified_prompt"] = (
            input_structure_info
            + context["prompt_text"]
            + " Return ONLY valid JSON. Do not include any surrounding text, Markdown code blocks, explanations, or a 'result' key.  Return the raw JSON data directly."
        )
    elif context["requested_format"] == "html":
        context["simplified_prompt"] = (
            input_structure_info
            + context["prompt_text"]
            + " Provide the data in a format suitable for an HTML structure. If generating a table, do not include the `<html>`, `<head>`, or `<body>` tags."
        )
    elif context["requested_format"] == "python":
        if context["output_intent"] == "code_only":
            context["simplified_prompt"] = (
                context["prompt_text"]
                + " Return *only* the Python code.  Do *not* include any explanations, "
                "comments *outside* of the code, example usage, or Markdown code fences (```).  "
                "Return *only* the raw, executable Python code."
            )
        elif context["output_intent"] == "code_with_explanation":
            context["simplified_prompt"] = (
                context["prompt_text"]
                + " Return the Python code, and include thorough comments in the code to explain the logic, as well as any relevant information outside the code"
            )
    else:  # Plaintext and other cases
        context["simplified_prompt"] = input_structure_info + context["prompt_text"]

    logger.debug(f"Request Context: {context}")
    return context

def _analyze_for_agent_prompt(prompt_text: str) -> tuple[Optional[str], Optional[str]]:
    """
    Analyzes the prompt text for agent-like instructions and deduces
    the output format and intent.  Returns (format, intent).
    """
    prompt_text_lower = prompt_text.lower()
    logger.debug(f"Analyzing for agent prompt. Prompt text: {prompt_text[:50]}...")  # Log the start of analysis
    deduced_format = None
    deduced_intent = None

    # General agent keywords
    agent_keywords = [
        "as a developer", "as a data scientist", "as a writer",
        "act as", "your role is", "you are a", "pretend to be",
        "simulate a", "emulate a", "behave like a"
    ]

    if any(keyword in prompt_text_lower for keyword in agent_keywords):
        logger.debug(f"Agent keywords detected: {', '.join(keyword for keyword in agent_keywords if keyword in prompt_text_lower)}") # Log detected keywords
        # Developer-related
        if any(keyword in prompt_text_lower for keyword in ["developer", "coder", "programmer", "write code", "develop a script", "create a function", "coding", "programming"]):
            deduced_format = "python"
            deduced_intent = "code_only"  # Default to code_only for developers
            logger.debug("Deduced format: python, Intent: code_only (developer agent)")

        # Data scientist-related
        elif any(keyword in prompt_text_lower for keyword in
                 ["data scientist", "statistician", "analyze data", "data analysis", "statistical analysis", "create a report"]):
            deduced_format = "json"  # Assume JSON for data analysis results
            deduced_intent = None
            logger.debug("Deduced format: json, Intent: None (data scientist agent)")

        # Writer-related
        elif any(keyword in prompt_text_lower for keyword in
                 ["writer", "author", "journalist", "write a story", "compose a poem", "draft an article", "narrative"]):
            deduced_format = "plaintext"
            deduced_intent = None
            logger.debug("Deduced format: plaintext, Intent: None (writer agent)")

    # --- JSON Specific Key Word Checks (Less reliable, place after agent roles) ---
    if not deduced_format:  # Only check if format hasn't already been determined
      if any(keyword in prompt_text_lower for keyword in
            ['"is_valid":','"message":', "response to critique"]):
        deduced_format = "json"
        deduced_intent = None
        logger.debug(f"Deduced format: json (JSON specific keywords)")
      if any(keyword in prompt_text_lower for keyword in
            ['"plan":', '"subtasks":', "generate the next set of subtasks", "planner agent"]):
        deduced_format = "json"
        deduced_intent = None
        logger.debug(f"Deduced format: json (Planner agent keywords)")
      if any(keyword in prompt_text_lower for keyword in
            ['"nodes":', '"edges":', "you are an expert in knowledge graph construction"]):
        deduced_format = "json"
        deduced_intent = None
        logger.debug(f"Deduced format: json (Knowledge graph agent keywords)")
      if any(keyword in prompt_text_lower for keyword in
            ['"answer":', '"score":', "assess the following response", "evaluate the quality"]):
        deduced_format = "json"
        deduced_intent = None
        logger.debug(f"Deduced format: json (Assessment keywords)")
      if any(keyword in prompt_text_lower for keyword in
            ['"role_name":', "you are an expert in agent-based systems", "suggest agent roles"]):
          deduced_format = "json"
          deduced_intent = None
          logger.debug(f"Deduced format: json (Role suggestion keywords)")

    if deduced_format or deduced_intent:
        logger.debug(f"Agent prompt analysis result - Format: {deduced_format}, Intent: {deduced_intent}")
    else:
        logger.debug("No agent prompt detected.")
    return deduced_format, deduced_intent


def _construct_prompt(prompt_text, requested_format, output_intent, input_structure_info):
    """Prompt construction function (no changes needed, logically correct)"""
    if requested_format == "json":
        prompt = (
            input_structure_info
            + prompt_text
            + " Return ONLY valid JSON. Do not include any surrounding text, Markdown code blocks, explanations, or a 'result' key.  Return the raw JSON data directly."
        )
    elif requested_format == "html":
        prompt = (
            input_structure_info
            + prompt_text
            + " Return HTML markup. Do not include surrounding text explaining the markup, just return valid HTML.  If generating a table, do not include the `<html>`, `<head>`, or `<body>` tags."
        )
    elif requested_format == "python":
        if output_intent == "code_only":
            prompt = (
                prompt_text
                + " Return *only* the Python code.  Do *not* include any explanations, "
                "comments *outside* of the code, example usage, or Markdown code fences (```).  "
                "Return *only* the raw, executable Python code."
            )
        elif output_intent == "code_with_explanation":
            prompt = (
                prompt_text
                + " Return the Python code, and include thorough comments in the code to explain the logic, as well as any relevant information outside the code"
            )
    else:  # Plaintext and other cases
        prompt = input_structure_info + prompt_text  # Plaintext, etc.

    logger.debug(f"Constructed simplified prompt for format '{requested_format}': {prompt[:1000]}...") # Log constructed prompt (truncated)

    return prompt