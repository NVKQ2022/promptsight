# 📚 PromptWright Documentation

Welcome to the **PromptWright** documentation. PromptWright is a production-grade, opinionated prompt engineering framework built on top of LangChain. It translates the rules of rigorous prompt engineering ([spec.md](spec.md)) into clean, reusable Python code.

---

## 🗺️ Documentation Directory Map

```text
docs/
├── architecture/             # Architectural principles, SOLID design, and design decisions
│   └── overview.md           # System architecture, protocol layers, and SOLID compliance
├── core/                     # Core API and prompt data model
│   ├── builder.md            # Fluent PromptBuilder API reference
│   └── sections.md           # PromptSections AST and prompt structure standard
├── middleware/               # Middleware pipeline and Quality Gate
│   └── overview.md           # Segregated protocols, AntiPatternValidator, and Grounding
├── renderers/                # Prompt compilation and token optimization
│   └── overview.md           # PromptRenderer, MarkdownSectionRenderer, and escaping
├── chains/                   # LangChain LCEL bridge and execution strategies
│   └── strategies.md         # ChainStrategy protocol (structured, pydantic, json, raw)
├── presets/                  # Production-hardened use case presets
│   ├── extraction.md         # Use Case 1: Structured Data Extraction
│   └── classification.md     # Use Case 2: Intent & Category Classification
├── few-shot/                 # Static and dynamic few-shot example selection
│   └── dynamic-selectors.md  # Dynamic vectorstore-backed example selection
├── evaluation/               # Golden Set evaluation and regression testing
│   └── regression-runner.md  # GoldenSetRunner, metrics, and CI/CD reporting
└── meta/                     # AI Prompt Engineering agent
    └── ai-prompt-generator.md# LLM-driven prompt generation from task description
```

---

## 🚀 Quick Navigation

| Topic | Document | Description |
|---|---|---|
| **Architecture** | [`architecture/overview.md`](architecture/overview.md) | How SOLID principles are implemented across PromptWright |
| **Builder Guide** | [`core/builder.md`](core/builder.md) | Step-by-step guide to constructing prompts with `PromptBuilder` |
| **AI Prompt Generator** | [`meta/ai-prompt-generator.md`](meta/ai-prompt-generator.md) | Using LLM to engineer prompts from user task descriptions |
| **Data Extraction** | [`presets/extraction.md`](presets/extraction.md) | Extracting structured entities without hallucination |
| **Classification** | [`presets/classification.md`](presets/classification.md) | Labeling and intent routing with strict taxonomy enforcement |
| **Quality Gate** | [`middleware/overview.md`](middleware/overview.md) | Compile-time anti-pattern detection (§15) and validation |
| **Token Optimization** | [`renderers/overview.md`](renderers/overview.md) | `tools_only` and `concise` modes saving ~60% prompt tokens |
| **Dynamic Few-Shot** | [`few-shot/dynamic-selectors.md`](few-shot/dynamic-selectors.md) | Using LangChain's `BaseExampleSelector` for semantic search |
| **Regression Testing** | [`evaluation/regression-runner.md`](evaluation/regression-runner.md) | Automated Golden Set benchmarking (§17) with Markdown reports |
