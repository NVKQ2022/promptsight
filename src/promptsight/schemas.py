"""Helpers for generating full and concise schema descriptions from Pydantic models (Challenge 1)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Literal, Type

from pydantic import BaseModel

SchemaMode = Literal["full", "concise", "tools_only"]


def generate_concise_schema_description(model: Type[BaseModel]) -> str:
    """Generates a compact field summary without verbose JSON Schema metadata."""
    schema = model.model_json_schema()
    properties: Dict[str, Any] = schema.get("properties", {})
    required: List[str] = schema.get("required", [])

    lines: List[str] = ["Return ONLY a JSON object containing the following fields:"]

    for field_name, field_info in properties.items():
        field_type = field_info.get("type")
        if not field_type and "$ref" in field_info:
            field_type = field_info["$ref"].split("/")[-1]
        elif field_type == "array":
            items = field_info.get("items", {})
            item_type = items.get("type") or items.get("$ref", "item").split("/")[-1]
            field_type = f"list[{item_type}]"

        req_label = "required" if field_name in required else "optional"
        desc = field_info.get("description", "")
        desc_part = f" — {desc}" if desc else ""
        lines.append(f"- `{field_name}` ({field_type}, {req_label}){desc_part}")

    lines.append("\nDo not add prose or markdown formatting outside the JSON object.")
    return "\n".join(lines)


def render_schema_format_text(
    model: Type[BaseModel],
    mode: SchemaMode = "full",
    escape_braces_for_fstring: bool = True,
) -> str:
    """Renders the appropriate output format text according to SchemaMode."""
    if mode == "tools_only":
        return (
            "Return the structured response matching the tool definition schema.\n"
            "Do not include any prose, markdown explanations, or text outside the structured call."
        )

    if mode == "concise":
        return generate_concise_schema_description(model)

    # mode == "full"
    schema_json = model.model_json_schema()
    schema_str = json.dumps(schema_json, indent=2)
    if escape_braces_for_fstring:
        schema_str = schema_str.replace("{", "{{").replace("}", "}}")

    return (
        "Return ONLY valid JSON strictly conforming to the following JSON schema:\n\n"
        f"```json\n{schema_str}\n```\n"
        "Do not include any prose, markdown explanations, or text outside the JSON."
    )
