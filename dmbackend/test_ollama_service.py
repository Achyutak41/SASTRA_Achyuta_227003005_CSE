
from app.ollama_service import (
    check_ollama_health,
    generate_completion,
)


def main():
    health = check_ollama_health()
    print("Ollama health:", health)

    if not health["available"]:
        raise SystemExit(
            "FAIL: Ollama is not reachable from the backend."
        )

    if not health["model_installed"]:
        raise SystemExit(
            "FAIL: Model not installed. Run "
            "'docker compose exec ollama ollama pull qwen2.5:3b'."
        )

    result = generate_completion(
        system_prompt="Answer briefly using only the evidence.",
        user_prompt=(
            "What does RTE provide? Evidence: RTE provides "
            "communication services to AUTOSAR application "
            "software components."
        ),
    )

    print("\nGenerated answer:")
    print(result["answer"])
    print("Model:", result["model"])

    if not result["answer"]:
        raise SystemExit("FAIL: Empty answer.")

    print("\nOLLAMA SERVICE TEST PASSED")


if __name__ == "__main__":
    main()
