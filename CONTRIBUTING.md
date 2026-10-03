# Contributing to PromptWright

Thank you for your interest in contributing to PromptWright! We welcome contributions ranging from bug fixes and documentation improvements to new anti-pattern validation rules and model presets.

---

## 🛠️ Development Setup

PromptWright uses [`uv`](https://docs.astral.sh/uv/) for high-speed dependency and virtualenv management, and Python ≥ 3.11.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NVKQ2022/promptwright.git
   cd promptwright
   ```

2. **Create and activate a virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. **Install editable package with development dependencies:**
   ```bash
   uv pip install -e ".[dev]"
   ```

---

## 🧪 Testing & Code Quality

Before submitting a pull request, ensure all tests, lint checks, and formatting pass cleanly:

```bash
# Run full test suite
pytest -v

# Run linter
ruff check src tests

# Check code formatting
ruff format --check src tests
```

To auto-format code:
```bash
ruff format src tests
ruff check --fix src tests
```

---

## 📝 Commit Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat(scope): ...` for new features or capabilities
- `fix(scope): ...` for bug fixes
- `docs(scope): ...` for documentation updates
- `test(scope): ...` for adding or improving tests
- `refactor(scope): ...` for code refactoring without behavior change
- `chore(scope): ...` for maintenance, tooling, or CI updates

---

## 💡 Proposing New Prompt Rules

When contributing a new anti-pattern detection rule:
1. Explain the rationale and cite relevant LLM vendor guidelines or benchmark evidence.
2. Implement the rule as a decoupled component implementing the `ValidationRule` protocol.
3. Provide unit tests covering positive cases (valid prompt passes) and negative cases (anti-pattern triggers warning/error).
4. Update rule documentation under `docs/middleware/`.
