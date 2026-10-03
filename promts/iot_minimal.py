"""Minimal LangChain prompt for IoT tool-choice dataset generation."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional

# 1. Output schema
class Sample(BaseModel):
    id: str = Field(description="e.g. iot_001")
    user_utterance: str
    tool: Optional[str] = Field(description="tool name from catalog or null for no_tool")
    arguments: dict = Field(default_factory=dict)
    reasoning: str

class Dataset(BaseModel):
    samples: List[Sample]

# 2. Prompt (f-string, per PromtEngineering.md)
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Senior IoT Dataset Engineer.
Your goal is to generate {num_samples} labeled samples to train an LLM to choose the correct IoT tool.

<tool_catalog>
{tool_catalog}
</tool_catalog>

Task:
1. Analyze the catalog
2. Generate exactly {num_samples} diverse user_utterance grounded in {domain}
3. Choose correct tool (or null for no_tool) with valid arguments per args_schema

Constraints:
- Use ONLY tools from <tool_catalog>
- Return ONLY valid JSON array, no prose
- Each sample: {{id, user_utterance, tool, arguments, reasoning}}

Output Format: JSON array of Sample schema
Example: {{"id":"iot_001","user_utterance":"Set bedroom to 22C","tool":"set_temperature","arguments":{{"device_id":"thermostat_bedroom","temperature":22}},"reasoning":"user wants to set temp"}}
"""),
    ("human", "Generate {num_samples} samples for domain={domain}.")
])

# 3. Chain
parser = JsonOutputParser(pydantic_object=Dataset)

def build_chain(llm):
    """LCEL chain: prompt -> llm -> parser"""
    return prompt | llm | parser

# 4. Example usage
if __name__ == "__main__":
    from langchain_core.language_models.fake_chat_models import FakeListChatModel
    import json

    tool_catalog = json.dumps([
        {"name": "set_temperature", "description": "Set thermostat", "args_schema": {"type": "object", "properties": {"device_id": {"type": "string"}, "temperature": {"type": "number"}}, "required": ["device_id", "temperature"]}},
        {"name": "control_light", "description": "Control light", "args_schema": {"type": "object", "properties": {"device_id": {"type": "string"}, "action": {"type": "string"}}, "required": ["device_id", "action"]}},
        {"name": "get_temperature", "description": "Get temp", "args_schema": {"type": "object", "properties": {"device_id": {"type": "string"}}, "required": ["device_id"]}}
    ])

    # Fake LLM for demo (no API key needed)
    fake_response = json.dumps({"samples": [
        {"id": "iot_001", "user_utterance": "Set bedroom to 22C", "tool": "set_temperature", "arguments": {"device_id": "thermostat_bedroom", "temperature": 22}, "reasoning": "explicit set temp intent"},
        {"id": "iot_002", "user_utterance": "Turn on living room light", "tool": "control_light", "arguments": {"device_id": "light_living_room", "action": "turn_on"}, "reasoning": "light control intent"}
    ]})
    llm = FakeListChatModel(responses=[fake_response])

    chain = build_chain(llm)
    result = chain.invoke({"tool_catalog": tool_catalog, "num_samples": 2, "domain": "smart_home"})
    print(result)
