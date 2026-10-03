"""Few-shot example management (PromtEngineering.md §9)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from promptwright.sections import Example


def format_example_payload(val: Any) -> str:
    """Format input/output payload for examples."""
    if isinstance(val, BaseModel):
        return val.model_dump_json(indent=2)
    if isinstance(val, (dict, list)):
        return json.dumps(val, indent=2, ensure_ascii=False)
    return str(val)
