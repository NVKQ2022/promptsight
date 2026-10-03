"""Intelligent string escaping utility for LangChain f-string templates."""

from __future__ import annotations

import re
from typing import Container, Optional


def escape_fstring_braces(
    text: str,
    allowed_variables: Optional[Container[str]] = None,
) -> str:
    """Escapes curly braces in a template string so LangChain does not crash on syntax like regex or JSON.

    - Tokens matching an allowed variable name (e.g. `{query}`) are preserved.
    - Already escaped braces (e.g. `{{` or `}}`) are preserved.
    - All other single braces (e.g. `\\d{3,4}`, `{"key": "value"}`) are safely escaped to `{{` or `}}`.

    Args:
        text: The raw template text to sanitize.
        allowed_variables: Set or collection of variable names that should remain replacement fields.

    Returns:
        Safe template string ready for LangChain's f-string parser.
    """
    if not text:
        return ""

    allowed_set = set(allowed_variables) if allowed_variables else set()

    # Step 1: Temporarily protect valid replacement fields and already-escaped braces
    placeholder_map: dict[str, str] = {}
    counter = 0

    def _protect(match: re.Match[str]) -> str:
        nonlocal counter
        content = match.group(0)
        token = f"__PW_PROTECTED_{counter}__"
        counter += 1
        placeholder_map[token] = content
        return token

    # Protect already escaped braces {{ and }}
    temp = re.sub(r"\{\{|\}\}", _protect, text)

    # Protect variables: e.g. {var_name}
    def _protect_var(match: re.Match[str]) -> str:
        nonlocal counter
        var_name = match.group(1)
        if allowed_variables is None or var_name in allowed_set:
            token = f"__PW_VAR_{counter}__"
            counter += 1
            placeholder_map[token] = match.group(0)
            return token
        return match.group(0)

    temp = re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", _protect_var, temp)

    # Step 2: Double remaining single { and }
    temp = temp.replace("{", "{{").replace("}", "}}")

    # Step 3: Restore protected tokens
    for token, orig in placeholder_map.items():
        temp = temp.replace(token, orig)

    return temp
