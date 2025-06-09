# config.py

# --- LLM API ---
LLM_API_ENDPOINT = "http://localhost:5015/ask"
LLM_API_TIMEOUT = 450  # Timeout for LLM API requests in seconds

# --- Defaults ---
DEFAULT_OUTPUT_FORMAT = "plaintext"  # Default output format if not specified

# --- Error Correction ---
ERROR_CORRECTION_RETRIES = 4  # Number of retries for error correction

# --- Language Configuration ---

# This dictionary maps language names (lowercase) to their configuration.
LANGUAGE_CONFIG = {
    "python": {
        "family": "scripting",
        "keywords": ["def", "class", "import", "for", "while", "if", "else", "try", "except", "finally", "return", "with", "as", "from", "lambda", "yield"],
        "comment_syntax": "#",
        "file_extension": ".py",
        "formatter": "black",  # Optional: external code formatter
    },
    "java": {
        "family": "imperative",
        "keywords": ["public", "class", "static", "void", "int", "String", "if", "else", "for", "while", "try", "catch", "finally", "return", "new", "import", "package"],
        "comment_syntax": "//",
        "file_extension": ".java",
        "formatter": "google-java-format",  # Optional
    },
    "javascript": {
        "family": "scripting",
        "keywords": ["const", "let", "var", "function", "if", "else", "for", "while", "return", "new", "class", "this", "try", "catch", "finally"],
        "comment_syntax": "//",
        "file_extension": ".js",
        "formatter": "prettier"  # Optional
    },
     "htmljavascript": {
        "family": "frontend",
        "keywords": ["div", "input", "function", "const", "let", "var",  "if", "else", "for", "while", "return", "new", "class", "this", "try", "catch", "finally", "<script>", "</script>", "<html>", "</html>", "<head>", "</head>", "<body>", "</body>", "<style>", "</style>", "class", "id", "src", "href", "onclick", "document"],
        "comment_syntax": "//",
        "file_extension": ".html"
    },
    "html": {
        "family": "markup",
        "keywords": ["html", "head", "body", "div", "p", "span", "a", "img", "table", "tr", "td", "th", "ul", "ol", "li", "form", "input", "button", "select", "option"],
        "comment_syntax": "<!-- -->",
        "file_extension": ".html",
    },
    "css": {
        "family": "styling",  # Or "web", or a new family
        "keywords": ["selector", "property", "value", "color", "background", "font", "margin", "padding", "border", "display", "position", "{", "}", ":", ";"],
        "comment_syntax": "/* */",
        "file_extension": ".css",
    },
    "sql": {
        "family": "data",  # or "database"
        "keywords": ["SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "CREATE", "TABLE", "JOIN", "GROUP BY", "ORDER BY", "AND", "OR", "NOT", "NULL"],
        "comment_syntax": "--",
        "file_extension": ".sql",
    },
    "c": {
        "family": "imperative",
        "keywords": ["int", "float", "char", "if", "else", "for", "while", "do", "return", "struct", "typedef", "#include"],
        "comment_syntax": "//",
        "file_extension": ".c",
    },
    "c++": {
        "family": "imperative",
        "keywords": ["int", "float", "double", "char", "class", "public", "private", "protected", "if", "else", "for", "while", "do", "return", "new", "delete", "#include"],
        "comment_syntax": "//",
        "file_extension": ".cpp",
    },
     "c#": {
        "family": "imperative",
        "keywords": ["class", "public", "static", "void", "int", "string", "if", "else", "for", "while", "foreach", "return", "new", "using", "namespace"],
        "comment_syntax": "//",
        "file_extension": ".cs",
    },
     "go": {
        "family": "imperative", # or "concurrent"
        "keywords": ["package", "import", "func", "var", "const", "if", "else", "for", "range", "return", "go", "chan", "select", "defer"],
        "comment_syntax": "//",
        "file_extension": ".go",
    },
      "ruby": {
        "family": "scripting",
        "keywords": ["def", "class", "module", "if", "else", "unless", "while", "for", "in", "do", "end", "return", "require", "puts"],
        "comment_syntax": "#",
        "file_extension": ".rb",
    },
    "php": {
        "family": "scripting",
        "keywords": ["<?php", "?>", "echo", "if", "else", "elseif", "while", "for", "foreach", "function", "class", "return", "$"],
        "comment_syntax": "//",  # Also supports /* */
        "file_extension": ".php",
    },
        "swift": {
            "family": "imperative",  # or "multi-paradigm"
            "keywords": ["let", "var", "func", "class", "struct", "enum", "if", "else", "for", "in", "while", "return", "import", "protocol"],
            "comment_syntax": "//",
            "file_extension": ".swift",
        },
        "kotlin": {
            "family": "imperative",  # or "multi-paradigm"
            "keywords": ["val", "var", "fun", "class", "object", "if", "else", "for", "in", "while", "return", "package", "import"],
            "comment_syntax": "//",
            "file_extension": ".kt",
        },
        "r": {
            "family": "statistical",
            "keywords": ["if", "else", "for", "in", "while", "repeat", "function", "return", "<-", "TRUE", "FALSE", "NULL"],
            "comment_syntax": "#",
            "file_extension": ".r",
        },
    "bash": {  # Or shell scripting
        "family": "scripting",
        "keywords": ["if", "then", "else", "fi", "for", "in", "do", "done", "while", "until", "case", "esac", "function", "echo", "#!/bin/bash"],
        "comment_syntax": "#",
        "file_extension": ".sh",
    },
        "typescript": {
            "family": "scripting",
            "keywords": ["const", "let", "var", "function", "if", "else", "for", "while", "return", "new", "class", "this", "try", "catch", "finally", "interface", "type"],
            "comment_syntax": "//",
            "file_extension": ".ts"
        },

    # Add more languages here...

}

# --- Structure Analysis ---
# Add any configuration needed by the structure.py file

# --- Other Configuration ---
# Add any other global configuration variables here

# Freeze the configuration to prevent accidental modification (optional)
def _deep_freeze(data):
    if isinstance(data, dict):
        return {k: _deep_freeze(v) for k, v in data.items()}
    elif isinstance(data, list):
        return tuple(_deep_freeze(x) for x in data)  # Convert to tuple
    return data

LANGUAGE_CONFIG = _deep_freeze(LANGUAGE_CONFIG)