# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Determinism and snapshot test suite (`tests/test_snapshot.py`) ensuring bit-for-bit reproducible prompt generation.
- Explicit middleware pipeline methods: `use_transformer()` and `use_validator()` on `PromptBuilder`.
- Direct prompt rendering helper methods `render_system()` and `render_user()` on `PromptBuilder`.
- PEP 561 `py.typed` typing marker for static type checkers (mypy/pyright).
- GitHub Actions CI workflow supporting Python 3.11, 3.12, and 3.13.
- Development tooling configuration (`ruff`) in `pyproject.toml`.
- Open-source governance files: `CONTRIBUTING.md`, `SECURITY.md`, and GitHub issue/PR templates.

### Changed
- Relocated personal IoT dataset generation artifacts into `examples/iot/`.
- Moved core prompt specification to `docs/spec.md` and updated all internal references.
- Replaced non-deterministic `set()` tag ordering in `MarkdownSectionRenderer` with order-preserving deduplication (`dict.fromkeys`).
- Updated minimum supported Python version to `3.11` in `pyproject.toml`.

### Fixed
- Fixed role article grammar formatting ("You are a" vs "You are an" vs pre-existing prefixes).
- Replaced silent `except Exception: pass` in `AIPromptGenerator` with structured logging and selective exception handling.
- Removed dry-run execution of user callables during registration in `PromptBuilder.use()`.
- Removed stale `llm.txt` documentation dump from repository root.

---

## [0.1.0] - 2026-10-03

### Added
- Core `PromptBuilder` API supporting fluent, section-driven prompt composition.
- `PromptSections` Abstract Syntax Tree (AST).
- `MarkdownSectionRenderer` with XML context tags and brace escaping.
- Anti-pattern validation system (`AntiPatternValidator`) with checks for vague verbs, decorative roles, and missing tasks.
- Middleware pipeline supporting composable transformers and validators.
- Dynamic few-shot selector integration.
- Schema token optimization modes (`full`, `concise`, `tools_only`).
- Golden set regression testing framework (`GoldenSet`, `GoldenSetRunner`).
- AI Prompt Generator meta-prompting module (`AIPromptGenerator`).
- Presets for structured extraction and classification.
