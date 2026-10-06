import sys
from pathlib import Path

import ollama


# =============================================================
# PROJECT PATHS
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RETRIEVAL_DIR = (
    PROJECT_ROOT / "Code" / "retrieval"
)

PROMPT_FILE = (
    PROJECT_ROOT
    / "Model_Prompts_Config"
    / "rag_prompt.txt"
)


# =============================================================
# IMPORT RETRIEVAL MODULE
# =============================================================

sys.path.insert(
    0,
    str(RETRIEVAL_DIR)
)

from search import load_retriever, search


# =============================================================
# CONFIGURATION
# =============================================================

OLLAMA_MODEL = "mistral:latest"

TOP_K = 5

TEMPERATURE = 0.0

# Minimum final retrieval score required for
# considering evidence reasonably relevant.
CONFIDENCE_THRESHOLD = 0.70


# =============================================================
# LOAD PROMPT
# =============================================================

def load_prompt():

    if not PROMPT_FILE.exists():

        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT_FILE}"
        )

    with open(
        PROMPT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# =============================================================
# BUILD GROUNDING CONTEXT
# =============================================================

def build_context(results):

    context_parts = []

    for result in results:

        context_parts.append(
            f"[Chunk ID: {result['chunk_id']}]\n"
            f"Source: {result['source']}\n"
            f"Chunk type: {result['chunk_type']}\n"
            f"Evidence: {result['text']}"
        )

    return "\n\n".join(
        context_parts
    )


# =============================================================
# CREATE PROMPT
# =============================================================

def create_prompt(
    question,
    context
):

    template = load_prompt()

    return template.format(
        question=question,
        context=context
    )


# =============================================================
# CALCULATE RETRIEVAL CONFIDENCE
# =============================================================

def calculate_confidence(results):

    if not results:

        return "LOW"

    top_score = results[0]["final_score"]

    # ---------------------------------------------------------
    # High confidence
    # ---------------------------------------------------------

    if top_score >= 0.85:

        return "HIGH"

    # ---------------------------------------------------------
    # Medium confidence
    # ---------------------------------------------------------

    if top_score >= CONFIDENCE_THRESHOLD:

        return "MEDIUM"

    # ---------------------------------------------------------
    # Low confidence
    # ---------------------------------------------------------

    return "LOW"


# =============================================================
# CHECK WHETHER EVIDENCE IS SUFFICIENT
# =============================================================

def evidence_is_sufficient(results):

    if not results:

        return False

    top_score = results[0]["final_score"]

    return top_score >= CONFIDENCE_THRESHOLD


# =============================================================
# GENERATE ANSWER USING OLLAMA
# =============================================================

def generate_answer(prompt):

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise AUTOSAR HLD "
                    "analysis assistant. "
                    "Answer using ONLY the supplied "
                    "AUTOSAR evidence. "
                    "Do not invent facts. "
                    "Do not create citations."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": TEMPERATURE
        }
    )

    return response["message"]["content"].strip()


# =============================================================
# BUILD VERIFIED CITATIONS
# =============================================================

def build_citations(results):

    citations = []

    for result in results:

        citation = (
            f"[{result['chunk_id']}] "
            f"{result['source']}"
        )

        if citation not in citations:

            citations.append(
                citation
            )

    return citations


# =============================================================
# MAIN RAG PIPELINE
# =============================================================

def main():

    print("=" * 60)
    print("AI-POWERED AUTOSAR HLD ANALYSIS ASSISTANT")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load retriever
    # ---------------------------------------------------------

    print("\nLoading retrieval model...")

    model, index, metadata = (
        load_retriever()
    )

    print(
        f"Indexed chunks: {index.ntotal}"
    )

    # ---------------------------------------------------------
    # User question
    # ---------------------------------------------------------

    question = input(
        "\nEnter your AUTOSAR question: "
    ).strip()

    if not question:

        print(
            "\nQuestion cannot be empty."
        )

        return

    # ---------------------------------------------------------
    # Retrieval
    # ---------------------------------------------------------

    print(
        "\nSearching AUTOSAR knowledge base..."
    )

    results = search(
        question,
        model,
        index,
        metadata,
        top_k=TOP_K
    )

    # ---------------------------------------------------------
    # No evidence
    # ---------------------------------------------------------

    if not results:

        print("\n" + "=" * 60)
        print("GROUNDED ANSWER")
        print("=" * 60)

        print(
            "\nThe provided AUTOSAR knowledge base "
            "does not contain sufficient evidence "
            "to answer this question."
        )

        print("\nConfidence: LOW")

        return

    # ---------------------------------------------------------
    # Calculate confidence
    # ---------------------------------------------------------

    confidence = calculate_confidence(
        results
    )

    sufficient = evidence_is_sufficient(
        results
    )

    # ---------------------------------------------------------
    # Display retrieved evidence
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("RETRIEVED AUTOSAR EVIDENCE")
    print("=" * 60)

    for position, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n[{position}] "
            f"Semantic: "
            f"{result['score']:.4f} "
            f"Final: "
            f"{result['final_score']:.4f}"
        )

        print(
            f"Chunk: {result['chunk_id']}"
        )

        print(
            f"Type: {result['chunk_type']}"
        )

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Text: {result['text']}"
        )

    # ---------------------------------------------------------
    # Insufficient evidence
    # ---------------------------------------------------------

    if not sufficient:

        print("\n" + "=" * 60)
        print("GROUNDED ANSWER")
        print("=" * 60)

        print(
            "\nThe provided AUTOSAR knowledge base "
            "does not contain sufficient evidence "
            "to answer this question."
        )

        print(
            f"\nConfidence: {confidence}"
        )

        print("\nEvidence considered:")

        for result in results[:3]:

            print(
                f"- [{result['chunk_id']}] "
                f"{result['source']}"
            )

        return

    # ---------------------------------------------------------
    # Build grounding context
    # ---------------------------------------------------------

    context = build_context(
        results
    )

    prompt = create_prompt(
        question,
        context
    )

    # ---------------------------------------------------------
    # Generate answer
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("GENERATING GROUNDED ANSWER")
    print("=" * 60)

    try:

        answer = generate_answer(
            prompt
        )

    except Exception as error:

        print(
            "\nOllama generation failed."
        )

        print(
            f"Error: {error}"
        )

        return

    # ---------------------------------------------------------
    # Build verified citations
    # ---------------------------------------------------------

    citations = build_citations(
        results[:3]
    )

    # ---------------------------------------------------------
    # Final answer
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("GROUNDED ANSWER")
    print("=" * 60)

    print(
        f"\n{answer}"
    )

    # ---------------------------------------------------------
    # Verified confidence
    # ---------------------------------------------------------

    print(
        f"\nConfidence: {confidence}"
    )

    # ---------------------------------------------------------
    # Verified citations
    # ---------------------------------------------------------

    print("\nEvidence:")

    for citation in citations:

        print(
            f"- {citation}"
        )

    print("\n" + "=" * 60)
    print("RAG COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()