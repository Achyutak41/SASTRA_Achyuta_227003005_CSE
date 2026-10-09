
import json
import os
import urllib.error
import urllib.request


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://ollama:11434",
).rstrip("/")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b",
)

OLLAMA_TIMEOUT = int(
    os.getenv("OLLAMA_TIMEOUT", "180")
)


class OllamaError(RuntimeError):
    """Raised when Ollama cannot generate a response."""


def generate_completion(
    system_prompt,
    user_prompt,
    temperature=0.1,
):
    """Generate a response using the configured Ollama model."""

    url = f"{OLLAMA_BASE_URL}/api/chat"

    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "options": {
            "temperature": temperature,
        },
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=OLLAMA_TIMEOUT,
        ) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:
        details = exc.read().decode(
            "utf-8",
            errors="replace",
        )
        raise OllamaError(
            f"Ollama HTTP error {exc.code}: {details}"
        ) from exc

    except urllib.error.URLError as exc:
        raise OllamaError(
            "Cannot connect to Ollama. Check that the "
            "Ollama container is running and the model "
            f"'{OLLAMA_MODEL}' is available. Details: {exc}"
        ) from exc

    except TimeoutError as exc:
        raise OllamaError(
            f"Ollama timed out after {OLLAMA_TIMEOUT} seconds."
        ) from exc

    except (json.JSONDecodeError, KeyError) as exc:
        raise OllamaError(
            "Ollama returned an invalid response."
        ) from exc

    message = data.get("message", {})
    content = message.get("content", "").strip()

    if not content:
        raise OllamaError(
            "Ollama returned an empty answer."
        )

    return {
        "answer": content,
        "model": data.get("model", OLLAMA_MODEL),
        "prompt_eval_count": data.get("prompt_eval_count"),
        "eval_count": data.get("eval_count"),
        "total_duration": data.get("total_duration"),
    }


def check_ollama_health():
    """Check whether the Ollama HTTP service is reachable."""
    request = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/tags",
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=10,
        ) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        models = [
            item.get("name", "")
            for item in data.get("models", [])
        ]

        return {
            "available": True,
            "configured_model": OLLAMA_MODEL,
            "model_installed": any(
                name == OLLAMA_MODEL
                or name.startswith(OLLAMA_MODEL + "-")
                for name in models
            ),
            "models": models,
        }

    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
    ):
        return {
            "available": False,
            "configured_model": OLLAMA_MODEL,
            "model_installed": False,
            "models": [],
        }
