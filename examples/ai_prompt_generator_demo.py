"""Example: Using an LLM to engineer prompts from user task descriptions (docs/spec.md §20)."""

import json
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from promptwright import generate_prompt_from_task


def main():
    print("=== Feature Demo: AI Prompt Generation from User Task ===\n")

    user_request = (
        "I need a prompt that takes an error log from a production server and extracts "
        "the root cause, error code, stack trace, and recommends a fix."
    )

    print(f"User Task Request:\n\"{user_request}\"\n")

    # In real usage, pass any live LangChain LLM:
    # from langchain_openai import ChatOpenAI
    # llm = ChatOpenAI(model="gpt-4o")

    # Simulated response adhering to docs/spec.md §20
    simulated_ai_response = {
        "role": "Senior Site Reliability Engineer & Incident Investigator",
        "goal": "diagnose production server error logs and extract structured incident data with recommended remediations",
        "inputs": {"error_log": "Raw multiline log snippet or stack trace"},
        "tasks": [
            "Step 1: Read the delimited <error_log> and identify the primary exception or fault.",
            "Step 2: Extract the exact error code, failing service, and relevant stack trace span.",
            "Step 3: Analyze the failure mechanism and formulate a high-confidence remediation recommendation.",
        ],
        "constraints": [
            "Extract only error codes and trace details explicitly present in <error_log>.",
            "If the root cause cannot be determined with certainty, set root_cause to 'unresolved' and list diagnostic next steps.",
            "Do not fabricate missing log lines.",
        ],
        "output_format": "JSON object with keys: error_code (str), failing_service (str), root_cause (str), recommended_fix (str).",
        "examples": [
            {
                "input_text": "FATAL 2026-10-02 04:12:01 auth-service [ERR_DB_TIMEOUT]: connection timeout to 10.0.1.4:5432",
                "output_text": '{"error_code": "ERR_DB_TIMEOUT", "failing_service": "auth-service", "root_cause": "Database connection timeout to primary PostgreSQL node", "recommended_fix": "Inspect network latency to 10.0.1.4 and verify Aurora connection pool capacity."}',
                "description": "Database connection timeout incident",
            }
        ],
        "verifications": [
            "Error code matches log verbatim",
            "Root cause is directly grounded in error_log",
            "No ungrounded speculation",
        ],
        "design_decisions": "Assigned specific SRE role. Decomposed into 3 stages: parse, extract, remediate. Added explicit 'unresolved' fallback rule.",
        "test_cases": [
            "Standard fatal log with error code",
            "Truncated log missing stack trace",
            "Multiple cascading errors in one log",
            "Warning log without error code",
            "Empty or unparseable text",
        ],
        "anti_patterns_avoided": [
            "Eliminated vague verb 'handle error'",
            "Prevented hallucinated root causes",
            "Enforced positive framing",
        ],
    }

    fake_llm = FakeListChatModel(responses=[json.dumps(simulated_ai_response)])

    # 1. Generate structured prompt specification
    spec = generate_prompt_from_task(
        user_task=user_request,
        llm=fake_llm,
        additional_context="Infrastructure: Kubernetes cluster running Go microservices.",
    )

    print("--- 1. Generated Prompt (Markdown per §19) ---")
    print(spec.to_markdown())

    print("\n--- 2. Design Decisions & Quality Gate (§20) ---")
    print(f"Rationale: {spec.design_decisions}")
    print(f"Anti-Patterns Avoided: {spec.anti_patterns_avoided}")
    print(f"Mental Test Cases: {spec.test_cases}")

    # 2. Convert directly to executable PromptBuilder
    builder = spec.to_builder()
    prompt = builder.build()
    messages = prompt.format_messages(error_log="FATAL: Out of memory in worker-3")
    print(f"\n--- 3. Compiled LangChain Prompt ({len(messages)} messages) ---")
    print(f"User message rendered: {messages[-1].content}")


if __name__ == "__main__":
    main()
