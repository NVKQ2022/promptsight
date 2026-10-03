# Chain Strategies & LCEL Bridge

The chain module ([`src/promptsight/chain.py`](../../src/promptsight/chain.py)) implements the **Strategy Pattern** to bind compiled `ChatPromptTemplate` instances to LangChain LLMs and output parsers.

---

## 🧩 `ChainStrategy` Protocol

```python
@runtime_checkable
class ChainStrategy(Protocol):
    def build(
        self,
        prompt: ChatPromptTemplate,
        llm: Any,
        schema: Optional[Type[BaseModel]] = None,
    ) -> RunnableSequence:
        ...
```

---

## ⚡ Built-in Strategies

PromptSight includes 4 standard execution modes:

### 1. `"structured"` (`StructuredChainStrategy`)
- **Engine**: `llm.with_structured_output(schema)`
- **Target**: Models with native function-calling/tool-calling support (OpenAI GPT-4o, Anthropic Claude 3.5, Google Gemini 2.0).
- **Output**: Returns an instance of your Pydantic model directly.
```python
chain = builder.to_chain(llm, mode="structured")
result: Invoice = chain.invoke({"doc": text})
```

### 2. `"pydantic"` (`PydanticChainStrategy`)
- **Engine**: `prompt | llm | PydanticOutputParser(pydantic_object=schema)`
- **Target**: Open-source models or providers without tool-calling, where output parsing is handled via format instructions and schema validation.
- **Output**: Validated Pydantic model instance.
```python
chain = builder.to_chain(llm, mode="pydantic")
```

### 3. `"json"` (`JsonChainStrategy`)
- **Engine**: `prompt | llm | JsonOutputParser()`
- **Target**: Parsing arbitrary JSON objects or arrays into standard Python dictionaries and lists.
- **Output**: Standard Python `dict` or `list`.
```python
chain = builder.to_chain(llm, mode="json")
result: dict = chain.invoke({"doc": text})
```

### 4. `"raw"` (`RawChainStrategy`)
- **Engine**: `prompt | llm | StrOutputParser()`
- **Target**: Free-form text generation, markdown tables, or raw string output.
- **Output**: Python `str`.
```python
chain = builder.to_chain(llm, mode="raw")
```

---

## 🔌 Registering Custom Strategies (Open/Closed Principle)

You can register custom execution strategies (e.g. streaming structured parsers, fallback chains, LangSmith metadata decorators) without modifying PromptSight:

```python
from langchain_core.runnables import RunnableLambda
from promptsight import ChainStrategy, register_chain_strategy

class UpperCaseStrategy(ChainStrategy):
    def build(self, prompt, llm, schema=None):
        return prompt | llm | RunnableLambda(lambda m: m.content.upper())

# Register globally
register_chain_strategy("uppercase", UpperCaseStrategy())

# Use via string name
chain = builder.to_chain(llm, mode="uppercase")

# Or pass strategy instance directly (Dependency Inversion)
chain = builder.to_chain(llm, mode=UpperCaseStrategy())
```
