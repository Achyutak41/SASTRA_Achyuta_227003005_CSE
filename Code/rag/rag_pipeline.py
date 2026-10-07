from pathlib import Path
import sys

import ollama
from audit_logger import log_query


# =============================================================
# PROJECT PATHS
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RETRIEVAL_DIR = (
    PROJECT_ROOT
    / "Code"
    / "retrieval"
)

PROMPT_FILE = (
    PROJECT_ROOT
    / "Model_Prompts_Config"
    / "rag_prompt.txt"
)


# =============================================================
# IMPORT RETRIEVAL MODULE
# =============================================================

if str(RETRIEVAL_DIR) not in sys.path:
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
# BUILD CONTEXT
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
# CREATE GROUNDED PROMPT
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
# CONFIDENCE
# =============================================================

def calculate_confidence(results):

    if not results:
        return "LOW"

    top_score = results[0]["final_score"]

    if top_score >= 0.85:
        return "HIGH"

    if top_score >= CONFIDENCE_THRESHOLD:
        return "MEDIUM"

    return "LOW"


# =============================================================
# EVIDENCE SUFFICIENCY
# =============================================================

def evidence_is_sufficient(results):

    if not results:
        return False

    top_score = results[0]["final_score"]

    return top_score >= CONFIDENCE_THRESHOLD


# =============================================================
# GENERATE ANSWER
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
# VERIFIED CITATIONS
# =============================================================

def build_citations(results):

    citations = []

    for result in results:

        citation = {
            "chunk_id": result["chunk_id"],
            "source": result["source"],
            "chunk_type": result["chunk_type"],
            "text": result["text"]
        }

        citations.append(
            citation
        )

    return citations


# =============================================================
# COMPLETE RAG PIPELINE
# =============================================================

def answer_question(
    question,
    model,
    index,
    metadata,
    top_k=TOP_K
):

    question = question.strip()

    if not question:

        raise ValueError(
            "Question cannot be empty."
        )

    # ---------------------------------------------------------
    # 1. Retrieve evidence
    # ---------------------------------------------------------

    results = search(
        question,
        model,
        index,
        metadata,
        top_k=top_k
    )

    # ---------------------------------------------------------
    # 2. Calculate confidence
    # ---------------------------------------------------------

    confidence = calculate_confidence(
        results
    )

    # ---------------------------------------------------------
    # 3. Check evidence
    # ---------------------------------------------------------

    sufficient = evidence_is_sufficient(
        results
    )

    # ---------------------------------------------------------
    # 4. Generate grounded answer
    # ---------------------------------------------------------

    if sufficient:

        context = build_context(
            results
        )

        prompt = create_prompt(
            question,
            context
        )

        answer = generate_answer(
            prompt
        )

    else:

        answer = (
            "The provided AUTOSAR knowledge base does "
            "not contain sufficient evidence to answer "
            "this question."
        )

    # ---------------------------------------------------------
    # 5. Verified evidence
    # ---------------------------------------------------------

    citations = build_citations(
        results[:3]
    )
    log_query(
        question=question,
        answer=answer,
        confidence=confidence,
        evidence_sufficient=sufficient,
        citations=citations
    )

    # ---------------------------------------------------------
    # 6. Return structured result
    # ---------------------------------------------------------

    return {
        "question": question,
        "answer": answer,
        "confidence": confidence,
        "evidence_sufficient": sufficient,
        "results": results,
        "citations": citations
    }


# =============================================================
# STANDALONE TEST
# =============================================================

def main():

    print("=" * 60)
    print("REUSABLE AUTOSAR RAG PIPELINE")
    print("=" * 60)

    print("\nLoading retrieval system...")

    model, index, metadata = load_retriever()

    print(
        f"Indexed chunks: {index.ntotal}"
    )

    question = input(
        "\nEnter your AUTOSAR question: "
    ).strip()

    if not question:

        print("No question entered.")

        return

    result = answer_question(
        question,
        model,
        index,
        metadata
    )

    print("\n" + "=" * 60)
    print("GROUNDED ANSWER")
    print("=" * 60)

    print(
        result["answer"]
    )

    print(
        f"\nConfidence: "
        f"{result['confidence']}"
    )

    print(
        f"Evidence sufficient: "
        f"{result['evidence_sufficient']}"
    )

    print("\nEvidence:")

    for citation in result["citations"]:

        print(
            f"- [{citation['chunk_id']}] "
            f"{citation['source']}"
        )


if __name__ == "__main__":
    main()