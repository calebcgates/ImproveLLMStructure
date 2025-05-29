import json
import logging
import os
from datetime import datetime
from typing import Dict, Union, Optional

logger = logging.getLogger(__name__)

class Learner:
    """
    Handles learning from interactions to improve system performance.
    Now updated to utilize the context data from interactions.
    """

    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.learning_data = []  # In-memory store for now; later, use a file or DB


    def learn_from_interaction(self, interaction_data: dict):
        """
        Logs interaction data and performs learning updates.
        Now receives the full interaction_data dictionary including 'context'.

        Args:
            interaction_data: A dictionary containing all relevant data
                              from a single interaction, including the 'context'.
        """
        self._log_interaction(interaction_data) # Log Everything
        self._update_learning_data(interaction_data) # Update Internal Data
        self._apply_learning(interaction_data) # Apply learning rules, pass interaction_data


    def _log_interaction(self, interaction_data: dict):
        """Logs interaction data to a file."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"interaction_{timestamp}.log"
        log_filepath = os.path.join(self.log_dir, log_filename)

        try:
            with open(log_filepath, "w") as log_file:
                json.dump(interaction_data, log_file, indent=4)
            logger.info(f"Interaction data logged to: {log_filepath}")
        except Exception as e:
            logger.error(f"Failed to write interaction log to file: {e}", exc_info=True)

    def _update_learning_data(self, interaction_data: dict):
        """
        Updates the internal learning data with the new interaction.
        Appends the full interaction data to the learning_data list.
        """
        self.learning_data.append(interaction_data)


    def _apply_learning(self, interaction_data: dict): #Pass interaction_data
        """
        Applies learning rules to update system behavior.
        Now receives interaction_data to access context and other details.
        This is a placeholder for the core learning logic.
        """

        context = interaction_data.get("context", {}) # Safely get context
        if not context:
            logger.warning("Context data not found in interaction_data for learning.")
            return # Exit if no context

        input_structure = context.get("input_structure")
        output_structure = interaction_data["universal_representation"].get("output_structure") #Access from interaction_data
        validation_result = interaction_data["validation_result"] #Access from interaction_data

        if input_structure is None or output_structure is None: # Skip if structure is missing.
            return


        # --- Example Basic Rule-Based Learning (Adjusted for Context) ---
        # Rule 1: Adjust confidence based on validation success/failure
        if isinstance(validation_result, bool):
            if validation_result: # Success
                input_structure["confidence"] = min(1.0, input_structure["confidence"] + 0.05)
                output_structure["confidence"] = min(1.0, output_structure["confidence"] + 0.05)
            else: # Failure
                input_structure["confidence"] = max(0.0, input_structure["confidence"] - 0.1)
                output_structure["confidence"] = max(0.0, output_structure["confidence"] - 0.1)
        elif isinstance(validation_result, dict) and "valid" in validation_result:
            if validation_result["valid"]: # Success
                input_structure["confidence"] = min(1.0, input_structure["confidence"] + 0.05)
                output_structure["confidence"] = min(1.0, output_structure["confidence"] + 0.05)
            else: # Failure
                input_structure["confidence"] = max(0.0, input_structure["confidence"] - 0.1)
                output_structure["confidence"] = max(0.0, output_structure["confidence"] - 0.1)

        # Rule 2: If CSV input is consistently misinterpreted, reduce confidence
        if input_structure["input_structure_type"] == "csv_input" and isinstance(validation_result, dict) and not validation_result["valid"] :
            if validation_result["error_type"] != "JSONDecodeError":  # i.e., the error *wasn't* due to bad JSON
                input_structure["confidence"] = max(0.0, input_structure["confidence"] - 0.1)

        # Rule 3: If we asked the LLM for format deduction, and it got it wrong, reduce confidence.
        if "llm_format_deduction_response" in context and context["llm_format_deduction_response"]: # Access from context
            llm_suggested_format = None
            try:
                ranked_formats = [f.strip().lower() for f in context["llm_format_deduction_response"].split(",") if f.strip()] # Access from context
                for fmt in ranked_formats:
                    if fmt in ["json", "html", "python", "plaintext"]:
                        llm_suggested_format = fmt
                        break

                if (llm_suggested_format and output_structure["output_structure_type"] != "unknown"):
                    output_type_prefix = output_structure["output_structure_type"].split("_")[0]

                    if llm_suggested_format != output_type_prefix and isinstance(validation_result, dict) and not validation_result["valid"]:
                        logger.info(f"LLM format suggestion was incorrect. Suggested: {llm_suggested_format}, Actual: {output_structure['output_structure_type']}")
                        # In a real system you would lower the confidence of format deduction.
            except Exception as e:
                logger.error(f"Error processing LLM format deduction for learning: {e}")

        # --- Example Logging of Context Data for Debugging ---
        logger.debug(f"Learning Applied for Interaction with Context: {context.keys()}") # Log keys in context
        if "output_intent" in context:
            logger.debug(f"  Output Intent: {context['output_intent']}")
        if "requested_format" in context:
            logger.debug(f"  Requested Format: {context['requested_format']}")
        # Log other relevant context data as needed for debugging learning rules.


        # --- Future: More Advanced Learning Rules (using Context) ---
        # Example: Improve prompt templates based on output_intent and requested_format
        # Example: Adjust parsing strategies based on input_structure and validation errors.
        pass


# Example Usage (for testing within this module):
if __name__ == "__main__":
    learner = Learner()

    # Simulate some interactions - now include context
    dummy_context_valid = {
        "input_structure": {"input_structure_type": "csv_input", "confidence": 0.9, "features": {}},
        "prompt_text": "Convert this CSV to JSON",
        "requested_format": "json",
        "llm_format_deduction_response": None,
        "output_intent": "code_with_explanation" #Example intent
    }
    dummy_representation_valid = {
        "output_structure": {"output_structure_type": "json_like_output", "confidence": 0.8, "features": {}},
        "text_content": None,
        "json_fields": {"a": 1, "b": 2},
        "code_snippets": None,
        "html_content": None

    }
    interaction_data1 = {
        "context": dummy_context_valid,
        "raw_llm_response": '{"a": 1, "b": 2}',  # Valid JSON
        "universal_representation": dummy_representation_valid,
        "transformed_output": '{\n    "a": 1,\n    "b": 2\n}',
        "validation_result": True,
        "error_corrector_output": None,
        "error": None,
    }

    dummy_context_invalid = {
        "input_structure": {"input_structure_type": "csv_input", "confidence": 0.9, "features": {}},
        "prompt_text": "Convert this CSV to JSON - but make it invalid",
        "requested_format": "json",
        "llm_format_deduction_response": None,
        "output_intent": "code_only" #Example intent
    }
    dummy_representation_invalid = {
        "output_structure": {"output_structure_type": "json_like_output", "confidence": 0.6, "features": {}},
        "text_content": None,
        "json_fields": None,
        "code_snippets": None,
        "html_content": None

    }
    interaction_data2 = {
        "context": dummy_context_invalid,
        "raw_llm_response": '{"a": 1, "b":',  # Invalid JSON
        "universal_representation": dummy_representation_invalid,
        "transformed_output": '{"error": "JSON transformation failed: Expecting value: line 1 column 10 (char 9)"}',
        "validation_result": {"valid": False, "error_type": "JSONDecodeError", "message": "Expecting value: line 1 column 10 (char 9)"},
        "error_corrector_output": None,
        "error": None,
    }

    learner.learn_from_interaction(interaction_data1)  # Valid interaction with context
    learner.learn_from_interaction(interaction_data2)  # Invalid interaction with context

    # Print the (in-memory) learning data to see the effect
    print(learner.learning_data) # Inspect learning data