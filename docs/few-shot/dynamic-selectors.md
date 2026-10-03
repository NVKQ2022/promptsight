# Few-Shot Learning & Dynamic Example Selectors

PromptWright provides first-class support for both in-memory few-shot examples and runtime retrieval-augmented few-shot selection ([`src/promptwright/few_shot.py`](../../src/promptwright/few_shot.py)).

---

## 📌 Static Examples

For standard few-shot prompting, add examples directly to the builder. PromptWright automatically normalizes Pydantic models, dictionaries, or strings into JSON:

```python
builder = (
    PromptBuilder()
    .role("Math Tutor")
    .task("Solve problem")
    .example(
        input_data="What is 15% of 80?",
        output_data={"calculation": "80 * 0.15", "result": 12},
    )
    .example(
        input_data="What is 20% of 50?",
        output_data={"calculation": "50 * 0.20", "result": 10},
    )
)
```

---

## 🔍 Dynamic Few-Shot (Vector-Search Ready)

When managing hundreds of labeled examples, hardcoding all of them into the prompt overflows context limits. **Dynamic Few-Shot** queries a vector database (such as Chroma, FAISS, or Pinecone) at runtime to inject only the *k* most relevant examples for each user query.

### Using LangChain `SemanticSimilarityExampleSelector`

```python
from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from promptwright import PromptBuilder

# 1. Example repository
example_bank = [
    {"input": "How do I reset my password?", "output": "account_access"},
    {"input": "Can you refund my last charge?", "output": "billing"},
    {"input": "The app crashes when I click submit.", "output": "bug_report"},
]

# 2. Vectorstore-backed selector
example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples=example_bank,
    embeddings=OpenAIEmbeddings(),
    vectorstore_cls=Chroma,
    k=2,  # Retrieve top 2 most similar examples
)

# 3. Attach to PromptBuilder
builder = (
    PromptBuilder()
    .role("Support Classifier")
    .task("Classify ticket")
    .inputs(input="User ticket")
    .example_selector(example_selector)
)

prompt = builder.build()
# At runtime, prompt dynamically queries Chroma and injects the top 2 examples!
```

### Protocol Compatibility (`ExampleSelectorAdapter`)
Any custom class implementing `select_examples(input_variables: dict) -> list[dict]` is automatically adapted into a LangChain `BaseExampleSelector`.
