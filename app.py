# app.py

import json
import logging
import traceback

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from config import DEFAULT_OUTPUT_FORMAT
from prompt_handler import handle_user_request
from llm_manager import send_prompt_to_llm
from output_parser import parse_llm_output
from format_transformer import get_transformer
from validator import validate_output
from error_corrector import correct_output
from learner import Learner

# Set logging level to DEBUG here
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

learner = Learner()

@app.post("/ask")
async def interpret(request: Request):
    context = {}  # Initialize context
    try:
        request_headers = dict(request.headers)
        request_body = await request.body()

        # Log the raw request (headers and body)
        logger.debug(f"Raw Request Headers: {request_headers}")
        logger.debug(f"Raw Request Body: {request_body.decode('utf-8', errors='ignore')}")

        context = await handle_user_request(request_headers, request_body)

        context_error = context.get('error')
        if context_error:
            logger.error(f"Error in request processing: {context_error}. Context: {context}")
            if context_error == "Missing question in JSON request":
                return PlainTextResponse("Error: The question is missing from your request.", status_code=400)
            elif context_error.startswith("Invalid JSON"):
                return PlainTextResponse(f"Error: Invalid JSON provided in request. {context_error}", status_code=400) # More details
            elif context_error.startswith("CSV"):
                return PlainTextResponse(f"Error: {context_error}", status_code=400)
            elif context_error.startswith("Unsupported content type"):
                return PlainTextResponse(f"Error: {context_error}", status_code=400)
            else:
                return PlainTextResponse(f"Error in request processing: {context_error}", status_code=400)  # More general 400

        simplified_prompt = context["simplified_prompt"]
        raw_llm_response = await send_prompt_to_llm(simplified_prompt)
        if raw_llm_response.startswith("Error:"):
            logger.error(f"LLM Error: {raw_llm_response}. Context: {context}")
            return PlainTextResponse(f"LLM Error: {raw_llm_response}", status_code=502) # LLM errors are 502

        requested_format = context["requested_format"]
        universal_representation = parse_llm_output(raw_llm_response, requested_format, context)

        transformer = get_transformer(requested_format)
        transformed_output = transformer.transform(universal_representation, context)
        logger.debug(f"Transformed output BEFORE validation: {transformed_output}")

        expected_structure = None
        if requested_format == "json" and context.get("prompt_text"): # Safer get()
            if "array" in context["prompt_text"].lower():
                expected_structure = "array"
            elif "object" in context["prompt_text"].lower():
                expected_structure = "object"

        validation_result = validate_output(transformed_output, requested_format, expected_structure)


        # --- Error Correction (if needed) ---
        error_corrector_output = None  # Initialize
        if isinstance(validation_result, dict) and not validation_result.get("valid"):
            logger.warning(f"Validation failed: {validation_result.get('error_type', 'Unknown')} - {validation_result.get('message', 'No message')}")
            error_corrector_output = await correct_output(universal_representation, requested_format, raw_llm_response, context, validation_result)
            if error_corrector_output:
                validation_result = validate_output(error_corrector_output, requested_format, expected_structure) # Re-validate
                if isinstance(validation_result, dict) and validation_result.get("valid"):
                    transformed_output = error_corrector_output # Use corrected output
                elif validation_result is True: #If is true
                    transformed_output = error_corrector_output # Use corrected output

        elif validation_result is False: # If valid is false
            logger.warning("Validation failed (boolean result).")
            error_corrector_output = await correct_output(universal_representation, requested_format, raw_llm_response, context, {})
            if error_corrector_output:
                validation_result = validate_output(error_corrector_output, requested_format, expected_structure)  # Re-validate
                if isinstance(validation_result, (bool, dict)) and (validation_result is True or (isinstance(validation_result, dict) and validation_result.get("valid", False))):
                    transformed_output = error_corrector_output

        interaction_data = {
            "context": context,
            "raw_llm_response": raw_llm_response,
            "universal_representation": universal_representation,
            "transformed_output": transformed_output,
            "validation_result": validation_result,  # Include validation_result
            "error_corrector_output": error_corrector_output,  # Include error_corrector_output
            "error": context.get("error"),  # Include any initial error
        }
        learner.learn_from_interaction(interaction_data)


        # --- Response Handling ---
        if isinstance(validation_result, bool) and validation_result:
            if requested_format == "json":
                try:
                    logger.debug(f"Returning JSON: {transformed_output}")
                    return JSONResponse(content=json.loads(transformed_output), media_type="application/json")
                except json.JSONDecodeError as e:
                    logger.exception(f"JSON DECODE ERROR AFTER VALIDATION: {e}. Output: {transformed_output}")
                    return PlainTextResponse(content=f"Error: Internal JSON encoding problem after validation. {e}", status_code=500) # More details
            elif requested_format == "html":
                logger.debug(f"Returning HTML: {transformed_output}")
                return HTMLResponse(content=transformed_output)
            elif requested_format == "python":
                logger.debug(f"Returning Python: {transformed_output}")
                return PlainTextResponse(content=transformed_output, media_type="text/x-python")
            else:
                logger.debug(f"Returning Plaintext: {transformed_output}")
                return PlainTextResponse(content=transformed_output)
        elif isinstance(validation_result, dict) and validation_result["valid"]:  # Handle dictionary result
            if requested_format == "json":
                try:
                    logger.debug(f"Returning JSON: {transformed_output}")
                    return JSONResponse(content=json.loads(transformed_output), media_type="application/json")
                except json.JSONDecodeError as e:
                    logger.exception(f"JSON DECODE ERROR AFTER VALIDATION: {e}. Output: {transformed_output}")
                    return PlainTextResponse(content=f"Error: Internal JSON encoding problem after validation. {e}", status_code=500)
            elif requested_format == "html":
                logger.debug(f"Returning HTML: {transformed_output}")
                return HTMLResponse(content=transformed_output)
            elif requested_format == "python":
                logger.debug(f"Returning Python: {transformed_output}")
                return PlainTextResponse(content=transformed_output, media_type="text/x-python")
            else:
                logger.debug(f"Returning Plaintext: {transformed_output}")
                return PlainTextResponse(content=transformed_output)


        else:
            logger.error(f"Final output still invalid. Returning best effort. Context: {context}, LLM Response: {raw_llm_response}")
            if requested_format == "json":
                # Attempt to return *something* as JSON, even if invalid
                try:
                    return JSONResponse(content=json.loads(transformed_output), status_code=500) # Still try
                except:
                    return PlainTextResponse(content="Error: Final output was not valid JSON and could not be parsed.", status_code=500)
            elif requested_format == "html":  # Still return HTML
                return HTMLResponse(content=transformed_output, status_code=500)
            else:
                return PlainTextResponse(content=transformed_output, status_code=500) # Best-effort return

    except Exception as e:
        logger.exception(f"Unhandled exception in /interpret: {e}")  # Use logger.exception
        return PlainTextResponse(content=f"Internal Server Error: {e}", status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5025)