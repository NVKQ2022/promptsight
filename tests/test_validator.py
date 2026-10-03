import pytest
from promptwright import PromptBuilder, AntiPatternValidator, IssueSeverity


def test_anti_pattern_vague_verb_detected():
    builder = (
        PromptBuilder()
        .role("Developer")
        .task("Handle the user input and process the file")
        .output_format("JSON")
    )
    issues = builder.validate(strict=False)
    vague_issues = [i for i in issues if i.code == "VAGUE_VERB"]
    assert len(vague_issues) >= 1
    assert "handle" in vague_issues[0].message.lower() or "process" in vague_issues[0].message.lower()


def test_decorative_role_detected():
    builder = (
        PromptBuilder()
        .role("an expert")
        .task("Generate unit tests")
        .output_format("Python code")
    )
    issues = builder.validate(strict=False)
    role_issues = [i for i in issues if i.code == "DECORATIVE_ROLE"]
    assert len(role_issues) == 1


def test_missing_task_causes_error_in_strict_mode():
    builder = (
        PromptBuilder()
        .role("Tester")
        .output_format("JSON")
    )
    # validate in non-strict gives ERROR severity
    issues = builder.validate(strict=False)
    error_issues = [i for i in issues if i.severity == IssueSeverity.ERROR]
    assert len(error_issues) == 1
    assert error_issues[0].code == "MISSING_TASK"

    # In strict mode, build() should raise ValueError
    with pytest.raises(ValueError, match="Prompt validation failed"):
        builder.build(strict=True)
