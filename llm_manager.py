# llm_manager.py
import httpx
import json
import asyncio
import logging
from config import LLM_API_ENDPOINT, LLM_API_TIMEOUT

logger = logging.getLogger(__name__)

async def send_prompt_to_llm(prompt: str) -> str:
    """
    Asynchronously sends a prompt to the LLM API and returns the raw response.

    Args:
        prompt: The prompt string to send to the LLM.

    Returns:
        The raw LLM response string, or an error message if the request fails.
    """
    headers = {"Content-Type": "application/json"}
    data = {"question": prompt}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LLM_API_ENDPOINT,
                headers=headers,
                json=data,
                timeout=LLM_API_TIMEOUT
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            llm_response_json = response.json()

            if "answer" in llm_response_json:
                return llm_response_json["answer"]
            else:  # Handle missing "answer" key
                error_message = f"Error: LLM response missing 'answer' field. Response: {llm_response_json}"
                logger.error(error_message)
                return f"Error: {error_message}"  # Prefix with "Error: " for consistent error handling

    except httpx.TimeoutException:
        error_message = "Error: Timeout while waiting for LLM response."
        logger.error(error_message)
        return f"Error: {error_message}"
    except httpx.RequestError as e:
        error_message = f"Error: Request error communicating with LLM API: {e}"
        logger.error(error_message)
        return f"Error: {error_message}"
    except httpx.HTTPStatusError as e:  # More specific HTTP error handling
        if e.response.status_code == 422:
             return "Error: LLM API rejected request (422 - Missing question)" # Specific error message for app.py
        else:
            error_message = f"Error: HTTP error communicating with LLM API: {e}"
            logger.error(error_message)
            return f"Error: {error_message}"
    except json.JSONDecodeError:
        error_message = "Error: Could not decode JSON response from LLM API."
        logger.error(error_message)
        return f"Error: {error_message}"
    except Exception as e:
        error_message = f"Error: An unexpected error occurred: {e}"
        logger.error(error_message)
        return f"Error: {error_message}"