from promptsight import (
    BaseMiddleware,
    PromptBuilder,
    PromptSections,
    StrictGroundingMiddleware,
)


class CustomTagMiddleware(BaseMiddleware):
    def transform(self, sections: PromptSections) -> PromptSections:
        sections.constraints.append("Custom constraint injected by middleware.")
        return sections


def test_custom_middleware_applied():
    builder = (
        PromptBuilder()
        .role("Reviewer")
        .task("Review code")
        .output_format("Markdown list")
        .use(CustomTagMiddleware())
    )
    prompt = builder.build()
    system_content = prompt.messages[0].prompt.template
    assert "Custom constraint injected by middleware." in system_content


def test_strict_grounding_middleware():
    builder = (
        PromptBuilder()
        .role("Extractor")
        .task("Extract dates")
        .output_format("JSON")
        .use(StrictGroundingMiddleware())
    )
    prompt = builder.build()
    system_content = prompt.messages[0].prompt.template
    assert "directly supported by the provided context" in system_content
    assert "Do not invent or guess facts" in system_content


def test_callable_middleware():
    def simple_middleware(sections: PromptSections) -> PromptSections:
        sections.verifications.append("Custom check")
        return sections

    builder = (
        PromptBuilder()
        .role("Editor")
        .task("Edit text")
        .output_format("Text")
        .use(simple_middleware)
    )
    prompt = builder.build()
    system_content = prompt.messages[0].prompt.template
    assert "- [ ] Custom check" in system_content
