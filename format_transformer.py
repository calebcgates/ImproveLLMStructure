# format_transformer.py
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

# --- Import Configuration ---
from config import LANGUAGE_CONFIG

logger = logging.getLogger(__name__)

# --- Abstract Base Class ---
class FormatTransformer(ABC):
    @abstractmethod
    def transform(self, universal_representation: dict, context: dict) -> str:
        pass

    @abstractmethod
    def can_handle(self, requested_format: str) -> bool:
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        pass

# --- Intermediate Abstract Classes ---

class ScriptingLanguageTransformer(FormatTransformer):
    def can_handle(self, requested_format: str) -> bool:
        return requested_format.lower() in self.get_supported_formats()

    def get_supported_formats(self) -> List[str]:
        supported_formats = []
        for language, config in LANGUAGE_CONFIG.items():
            if config.get("family") == "scripting":
                supported_formats.append(language)
        return supported_formats

class ImperativeLanguageTransformer(FormatTransformer):
    def can_handle(self, requested_format: str) -> bool:
        return requested_format.lower() in self.get_supported_formats()

    def get_supported_formats(self) -> List[str]:
        supported_formats = []
        for language, config in LANGUAGE_CONFIG.items():
            if config.get("family") == "imperative":
                supported_formats.append(language)
        return supported_formats

class MarkupLanguageTransformer(FormatTransformer):
    def can_handle(self, requested_format: str) -> bool:
        return requested_format.lower() in self.get_supported_formats()

    def get_supported_formats(self) -> List[str]:
        supported_formats = []
        for language, config in LANGUAGE_CONFIG.items():
            if config.get("family") == "markup":
                supported_formats.append(language)
        return supported_formats

class DataOrientedLanguageTransformer(FormatTransformer):  # For SQL, etc.
    def can_handle(self, requested_format: str) -> bool:
        return requested_format.lower() in self.get_supported_formats()

    def get_supported_formats(self) -> List[str]:
        supported_formats = []
        for language, config in LANGUAGE_CONFIG.items():
            if config.get("family") == "data":  # or "database" if you prefer
                supported_formats.append(language)
        return supported_formats

class StylingLanguageTransformer(FormatTransformer):
    def can_handle(self, requested_format: str) -> bool:
        return requested_format.lower() in self.get_supported_formats()
    def get_supported_formats(self) -> List[str]:
        supported_formats = []
        for language, config in LANGUAGE_CONFIG.items():
            if config.get("family") == "styling":
                supported_formats.append(language)
        return supported_formats

class FrontendLanguageTransformer(FormatTransformer):
    def can_handle(self, requested_format: str) -> bool:
        return requested_format.lower() in self.get_supported_formats()

    def get_supported_formats(self) -> List[str]:
        supported_formats = []
        for language, config in LANGUAGE_CONFIG.items():
            if config.get("family") == "frontend":
                supported_formats.append(language)
        return supported_formats

class StatisticalLanguageTransformer(FormatTransformer):
    def can_handle(self, requested_format: str) -> bool:
        return requested_format.lower() in self.get_supported_formats()
    def get_supported_formats(self) -> List[str]:
        supported_formats = []
        for language, config in LANGUAGE_CONFIG.items():
            if config.get("family") == "statistical":
                supported_formats.append(language)
        return supported_formats
        
class FunctionalLanguageTransformer(FormatTransformer): #Added
    def can_handle(self, requested_format: str) -> bool:
        return requested_format.lower() in self.get_supported_formats()

    def get_supported_formats(self) -> List[str]:
        supported_formats = []
        for language, config in LANGUAGE_CONFIG.items():
            if config.get("family") == "functional":
                supported_formats.append(language)
        return supported_formats


# --- Concrete Transformer Classes ---

class PlainTextTransformer(FormatTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
        return universal_representation.get("text_content", "").strip()

    def can_handle(self, requested_format: str) -> bool:
        return requested_format.lower() == "plaintext"

    def get_supported_formats(self) -> List[str]:
        return ["plaintext"]

class JSONTransformer(FormatTransformer):  # No inheritance needed
    def transform(self, universal_representation: dict, context: dict) -> str:
        try:
            if universal_representation["json_fields"] is not None:
                # Ensure json_fields is serializable
                if isinstance(universal_representation["json_fields"], (dict, list, str, int, float, bool, type(None))):
                     return json.dumps(universal_representation["json_fields"], indent=4, ensure_ascii=False).strip()
                else:
                    logger.warning(f"Unexpected type in json_fields: {type(universal_representation['json_fields'])}")
                    return json.dumps(
                        {"error": f"Unexpected data type in json_fields: {type(universal_representation['json_fields'])}"},
                        indent=4,
                        ensure_ascii=False,
                    )
            elif universal_representation["text_content"] is not None:
                try:
                    return json.dumps(json.loads(universal_representation["text_content"]), indent=4, ensure_ascii=False).strip()
                except json.JSONDecodeError:
                    return json.dumps({"result": universal_representation["text_content"]}, indent=4, ensure_ascii=False).strip()
            else:
                return json.dumps({"error": "No data to transform to JSON."}, indent=4, ensure_ascii=False).strip()
        except Exception as e:
            logger.exception(f"JSON transformation error: {e}")  # Use logger.exception for stack trace
            return json.dumps({"error": str(e)}, indent=4, ensure_ascii=False).strip()  # Ensure string return

    def can_handle(self, requested_format: str) -> bool:
        return requested_format.lower() == "json"

    def get_supported_formats(self) -> List[str]:
        return ["json"]


class HTMLTransformer(MarkupLanguageTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
        # Prioritize html_content, then json_fields, then text_content, then fallback.
        if universal_representation["html_content"] is not None:
            return universal_representation["html_content"].strip()
        elif universal_representation["json_fields"] is not None:
            # Very basic JSON-to-HTML table conversion
            try:
                if isinstance(universal_representation["json_fields"], list):
                    # Assume list of dictionaries
                    if not universal_representation["json_fields"]:  # Empty list
                        return "<p>No data available.</p>"
                    keys = universal_representation["json_fields"][0].keys()
                    html = "<table>\n"
                    html += "  <thead>\n    <tr>\n"
                    for key in keys:
                        html += f"      <th>{key}</th>\n"
                    html += "    </tr>\n  </thead>\n"
                    html += "  <tbody>\n"
                    for item in universal_representation["json_fields"]:
                        html += "    <tr>\n"
                        for key in keys:
                            html += f"      <td>{item.get(key, '')}</td>\n"  # Handle missing keys gracefully
                        html += "    </tr>\n"
                    html += "  </tbody>\n</table>"
                    return html.strip()
                elif isinstance(universal_representation["json_fields"], dict):
                    # Simple key-value table
                    html = "<table>\n"
                    for key, value in universal_representation["json_fields"].items():
                        html += f"  <tr><td>{key}</td><td>{value}</td></tr>\n"
                    html += "</table>"
                    return html.strip()
                else:
                     return f"<p>Unsupported JSON data type for HTML conversion: {type(universal_representation['json_fields'])}</p>"

            except Exception as e:
                logger.exception(f"Error during JSON to HTML conversion: {e}")  # Use logger.exception
                return f"<p>Error converting JSON to HTML: {e}</p>"

        elif universal_representation["text_content"] is not None:
            # Basic escaping and paragraph formatting
            return f"<p>{universal_representation['text_content'].replace('<', '<').replace('>', '>').replace('&', '&').replace(chr(10), '<br>')}</p>".strip()
        else:
            return "<p>No data available.</p>".strip()

    def can_handle(self, requested_format: str) -> bool:
        return requested_format.lower() == 'html'

    def get_supported_formats(self) -> list[str]:
        return ["html"]

class PythonTransformer(ScriptingLanguageTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
            return "\n".join(universal_representation.get("code_snippets", [])).strip()
        else:
            code = "\n".join(universal_representation.get("code_snippets", []))
            text = universal_representation.get("text_content", "")
            return (code + "\n" + text).strip() # Combine code and text

class JavaTransformer(ImperativeLanguageTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
         if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        #Very Basic just to get it to pass
         java_code = ""
         if universal_representation["code_snippets"]:
            java_code = "\n".join(universal_representation["code_snippets"])
         elif universal_representation["text_content"]:
            java_code = "//" + universal_representation["text_content"].replace("\n", "\n//")
         return java_code.strip()


class JavascriptTransformer(ScriptingLanguageTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
         if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        #Very Basic just to get it to pass
         js_code = ""
         if universal_representation["code_snippets"]:
            js_code = "\n".join(universal_representation["code_snippets"])
         elif universal_representation["text_content"]:
            js_code = "//" + universal_representation["text_content"].replace("\n", "\n//")
         return js_code.strip()

class HTMLJavascriptTransformer(FrontendLanguageTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
        # VERY basic example: combines HTML and Javascript.  You'll need much more sophisticated logic.
        html_part = universal_representation.get("html_content", "")
        js_part = "\n".join(universal_representation.get("code_snippets", []))

        combined = ""
        if html_part:
            combined += html_part + "\n"
        if js_part:
            combined += "<script>\n" + js_part + "\n</script>"
        return combined.strip()


class CTransformer(ImperativeLanguageTransformer):
     def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        #Very Basic just to get it to pass
        c_code = ""
        if universal_representation["code_snippets"]:
            c_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            c_code = "//" + universal_representation["text_content"].replace("\n", "\n// ")
        return c_code.strip()

class CppTransformer(ImperativeLanguageTransformer):
     def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        #Very Basic just to get it to pass
        cpp_code = ""
        if universal_representation["code_snippets"]:
            cpp_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            cpp_code = "//" + universal_representation["text_content"].replace("\n", "\n// ")
        return cpp_code.strip()

class CSharpTransformer(ImperativeLanguageTransformer):
     def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        #Very Basic just to get it to pass
        csharp_code = ""
        if universal_representation["code_snippets"]:
            csharp_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            csharp_code = "//" + universal_representation["text_content"].replace("\n", "\n// ")
        return csharp_code.strip()

class GoTransformer(ImperativeLanguageTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        #Very Basic just to get it to pass
        go_code = ""
        if universal_representation["code_snippets"]:
            go_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            go_code = "//" + universal_representation["text_content"].replace("\n", "\n// ")
        return go_code.strip()

class RubyTransformer(ScriptingLanguageTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        #Very Basic just to get it to pass
        ruby_code = ""
        if universal_representation["code_snippets"]:
            ruby_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            ruby_code = "#" + universal_representation["text_content"].replace("\n", "\n# ")
        return ruby_code.strip()

class PHPTransformer(ScriptingLanguageTransformer):
     def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        #Very Basic just to get it to pass
        php_code = ""
        if universal_representation["code_snippets"]:
            php_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            php_code = "//" + universal_representation["text_content"].replace("\n", "\n// ")
        return php_code.strip()

class SwiftTransformer(ImperativeLanguageTransformer):
     def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        swift_code = ""
        if universal_representation["code_snippets"]:
            swift_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            swift_code = "// " + universal_representation["text_content"].replace("\n", "\n// ")
        return swift_code.strip()

class KotlinTransformer(ImperativeLanguageTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        kotlin_code = ""
        if universal_representation["code_snippets"]:
            kotlin_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            kotlin_code = "// " + universal_representation["text_content"].replace("\n", "\n// ")
        return kotlin_code.strip()

class RTransformer(StatisticalLanguageTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        r_code = ""
        if universal_representation["code_snippets"]:
            r_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            r_code = "# " + universal_representation["text_content"].replace("\n", "\n# ")
        return r_code.strip()

class BashTransformer(ScriptingLanguageTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        bash_code = ""
        if universal_representation["code_snippets"]:
            bash_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            bash_code = "# " + universal_representation["text_content"].replace("\n", "\n# ")
        return bash_code.strip()
class TypescriptTransformer(ScriptingLanguageTransformer):
      def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        ts_code = ""
        if universal_representation["code_snippets"]:
            ts_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            ts_code = "// " + universal_representation["text_content"].replace("\n", "\n// ")
        return ts_code.strip()

class CSSTransformer(StylingLanguageTransformer):
     def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
             return "\n".join(universal_representation.get("code_snippets", [])).strip()
        css_code = ""
        if universal_representation["code_snippets"]:
            css_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            css_code = "/* " + universal_representation["text_content"].replace("\n", "\n/* ") + " */"
        return css_code.strip()

class SQLTransformer(DataOrientedLanguageTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
        if context.get("output_intent") == "code_only":
            return "\n".join(universal_representation.get("code_snippets", [])).strip()
        sql_code = ""
        if universal_representation["code_snippets"]:
            sql_code = "\n".join(universal_representation["code_snippets"])
        elif universal_representation["text_content"]:
            sql_code = "-- " + universal_representation["text_content"].replace("\n", "\n-- ")
        return sql_code.strip()

class DefaultTransformer(FormatTransformer):
    def transform(self, universal_representation: dict, context: dict) -> str:
        # Always return a string, even if text_content is None
        return str(universal_representation.get("text_content", "Unsupported format or no content.")).strip()

    def can_handle(self, requested_format: str) -> bool:
        return False  # Never the primary handler

    def get_supported_formats(self) -> List[str]:
        return []  # Supports no specific formats


# --- Transformer Mapping (Crucial for Dynamic Selection) ---
TRANSFORMER_MAP = {
    "python": PythonTransformer(),  # Instantiate here
    "java": JavaTransformer(),
    "javascript": JavascriptTransformer(),
    "htmljavascript": HTMLJavascriptTransformer(),
    "html": HTMLTransformer(),
    "css": CSSTransformer(),
    "sql": SQLTransformer(),
    "c": CTransformer(),
    "c++": CppTransformer(),
    "c#": CSharpTransformer(),
    "go": GoTransformer(),
    "ruby": RubyTransformer(),
    "php": PHPTransformer(),
    "swift": SwiftTransformer(),
    "kotlin": KotlinTransformer(),
    "r": RTransformer(),
    "bash": BashTransformer(),
    "typescript": TypescriptTransformer(),
     "json": JSONTransformer(),  # Add JSONTransformer
    "plaintext": PlainTextTransformer(), # Add PlainTextTransformer
    # Add other mappings
}

# --- get_transformer Function ---
def get_transformer(requested_format: str) -> Optional[FormatTransformer]:
    """
    Returns the appropriate transformer instance based on the requested format.
    Falls back to DefaultTransformer if no specific transformer is found.
    """
    requested_format = requested_format.lower()  # Ensure lowercase
    transformer_instance = TRANSFORMER_MAP.get(requested_format)
    if transformer_instance:
        return transformer_instance
    else:
        logger.warning(f"No specific transformer found for format: {requested_format}, using DefaultTransformer.")
        return PlainTextTransformer() # Default transformer (handles text)