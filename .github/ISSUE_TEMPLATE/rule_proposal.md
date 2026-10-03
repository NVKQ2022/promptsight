---
name: Prompt validation rule proposal
about: Propose a new static prompt anti-pattern rule or quality check
title: "[RULE] "
labels: rule, enhancement
assignees: ''
---

**Rule Name & Proposed Code**
- Rule name (e.g. `MISSING_VARIABLE_DELIMITER`):
- Category (Syntax / Anti-Pattern / Grounding / Security):

**What prompt issue does this rule detect?**
Describe the prompt pattern that leads to degraded LLM performance, hallucinations, or prompt injection vulnerability.

**Evidence & Rationale**
Cite vendor guidance (Anthropic/OpenAI/Google), research papers, or empirical observations:
- Source link 1:
- Source link 2:

**Sample Positive Example (Should pass)**
```markdown
# Role & Goal
You are a Data Classifier.
```

**Sample Negative Example (Should trigger warning/error)**
```markdown
You are an expert coder that does stuff.
```

**Proposed Severity**
- [ ] Warning
- [ ] Error
- [ ] Info
