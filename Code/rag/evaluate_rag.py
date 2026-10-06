import json
import re
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

QUESTIONS_FILE = (
    PROJECT_ROOT
    / "Evaluation_Results"
    / "rag_evaluation_questions.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "Evaluation_Results"
    / "rag_evaluation_results.json"
)

PROMPT_FILE = (
    PROJECT_ROOT
    / "Model_Prompts_Config"
    / "rag_prompt.txt"
)


# =============================================================
# IMPORT RETRIEVAL
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

CONFIDENCE_THRESHOLD = 0.70


# =============================================================
# LOAD QUESTIONS
# =============================================================

def load_questions():

    if not QUESTIONS_FILE.exists():

        raise FileNotFoundError(
            f"Evaluation questions not found: "
            f"{QUESTIONS_FILE}"
        )

    with open(
        QUESTIONS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =============================================================
# LOAD PROMPT
# =============================================================

def load_prompt():

    if not PROMPT_FILE.exists():

        raise FileNotFoundError(
            f"Prompt file not found: "
            f"{PROMPT_FILE}"
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
# GENERATE ANSWER
# =============================================================

def generate_answer(
    question,
    context,
    prompt_template
):

    prompt = prompt_template.format(
        question=question,
        context=context
    )

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise AUTOSAR HLD "
                    "analysis assistant. "
                    "Use only the supplied evidence. "
                    "Do not invent facts. "
                    "Do not generate citations."
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

    return response[
        "message"
    ][
        "content"
    ].strip()


# =============================================================
# KEYWORD CHECK
# =============================================================

def keyword_check(
    answer,
    expected_keywords
):

    answer_lower = answer.lower()

    missing = []

    for keyword in expected_keywords:

        if keyword.lower() not in answer_lower:

            missing.append(
                keyword
            )

    return (
        len(missing) == 0,
        missing
    )


# =============================================================
# REFUSAL CHECK
# =============================================================

def refusal_check(answer):

    refusal_phrases = [
        "does not contain sufficient evidence",
        "insufficient evidence",
        "not enough evidence",
        "cannot determine from the provided evidence"
    ]

    answer_lower = answer.lower()

    return any(
        phrase in answer_lower
        for phrase in refusal_phrases
    )


# =============================================================
# MAIN EVALUATION
# =============================================================

def main():

    print("=" * 60)
    print("AUTOSAR RAG EVALUATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load questions
    # ---------------------------------------------------------

    questions = load_questions()

    prompt_template = load_prompt()

    # ---------------------------------------------------------
    # Load retrieval system
    # ---------------------------------------------------------

    print("\nLoading retrieval model...")

    model, index, metadata = (
        load_retriever()
    )

    print(
        f"Indexed chunks: {index.ntotal}"
    )

    # ---------------------------------------------------------
    # Evaluation counters
    # ---------------------------------------------------------

    answer_tests = 0
    answer_passed = 0

    refusal_tests = 0
    refusal_passed = 0

    results_output = []

    # ---------------------------------------------------------
    # Run each question
    # ---------------------------------------------------------

    for item in questions:

        question_id = item["id"]

        question = item["question"]

        expected_keywords = item[
            "expected_keywords"
        ]

        expected_behavior = item[
            "expected_behavior"
        ]

        print("\n" + "-" * 60)

        print(
            f"{question_id}: {question}"
        )

        # -----------------------------------------------------
        # Retrieval
        # -----------------------------------------------------

        results = search(
            question,
            model,
            index,
            metadata,
            top_k=TOP_K
        )

        # -----------------------------------------------------
        # Handle no retrieval
        # -----------------------------------------------------

        if not results:

            answer = (
                "The provided AUTOSAR knowledge base "
                "does not contain sufficient evidence "
                "to answer this question."
            )

            top_score = 0.0

        else:

            top_score = results[0][
                "final_score"
            ]

        # -----------------------------------------------------
        # Confidence
        # -----------------------------------------------------

        if top_score >= 0.85:

            confidence = "HIGH"

        elif top_score >= CONFIDENCE_THRESHOLD:

            confidence = "MEDIUM"

        else:

            confidence = "LOW"

        # -----------------------------------------------------
        # Refusal based on retrieval
        # -----------------------------------------------------

        if (
            expected_behavior == "refuse"
            and top_score < CONFIDENCE_THRESHOLD
        ):

            answer = (
                "The provided AUTOSAR knowledge base "
                "does not contain sufficient evidence "
                "to answer this question."
            )

        # -----------------------------------------------------
        # Generate answer
        # -----------------------------------------------------

        elif top_score >= CONFIDENCE_THRESHOLD:

            context = build_context(
                results
            )

            answer = generate_answer(
                question,
                context,
                prompt_template
            )

        # -----------------------------------------------------
        # Low-evidence refusal
        # -----------------------------------------------------

        else:

            answer = (
                "The provided AUTOSAR knowledge base "
                "does not contain sufficient evidence "
                "to answer this question."
            )

        # -----------------------------------------------------
        # Evaluate answer behavior
        # -----------------------------------------------------

        if expected_behavior == "answer":

            answer_tests += 1

            passed, missing = keyword_check(
                answer,
                expected_keywords
            )

            if passed:

                answer_passed += 1

                result_status = "PASS"

            else:

                result_status = "FAIL"

        else:

            refusal_tests += 1

            passed = refusal_check(
                answer
            )

            if passed:

                refusal_passed += 1

                result_status = "PASS"

            else:

                result_status = "FAIL"

            missing = []

        # -----------------------------------------------------
        # Display
        # -----------------------------------------------------

        print(
            f"Result: {result_status}"
        )

        print(
            f"Confidence: {confidence}"
        )

        print(
            f"Top retrieval score: "
            f"{top_score:.4f}"
        )

        print(
            f"Answer: {answer}"
        )

        # -----------------------------------------------------
        # Store result
        # -----------------------------------------------------

        retrieved_chunks = []

        for result in results:

            retrieved_chunks.append(
                result["chunk_id"]
            )

        results_output.append({

            "id": question_id,

            "question": question,

            "expected_behavior":
                expected_behavior,

            "expected_keywords":
                expected_keywords,

            "answer": answer,

            "confidence":
                confidence,

            "top_retrieval_score":
                top_score,

            "retrieved_chunks":
                retrieved_chunks,

            "missing_keywords":
                missing,

            "result":
                result_status

        })

    # =========================================================
    # CALCULATE METRICS
    # =========================================================

    if answer_tests > 0:

        answer_accuracy = (
            answer_passed
            / answer_tests
            * 100
        )

    else:

        answer_accuracy = 0.0

    if refusal_tests > 0:

        refusal_accuracy = (
            refusal_passed
            / refusal_tests
            * 100
        )

    else:

        refusal_accuracy = 0.0

    total_tests = (
        answer_tests
        + refusal_tests
    )

    total_passed = (
        answer_passed
        + refusal_passed
    )

    if total_tests > 0:

        overall_accuracy = (
            total_passed
            / total_tests
            * 100
        )

    else:

        overall_accuracy = 0.0

    # =========================================================
    # SUMMARY
    # =========================================================

    summary = {

        "total_tests":
            total_tests,

        "answer_tests":
            answer_tests,

        "answer_passed":
            answer_passed,

        "answer_accuracy":
            round(
                answer_accuracy,
                2
            ),

        "refusal_tests":
            refusal_tests,

        "refusal_passed":
            refusal_passed,

        "refusal_accuracy":
            round(
                refusal_accuracy,
                2
            ),

        "overall_passed":
            total_passed,

        "overall_accuracy":
            round(
                overall_accuracy,
                2
            )
    }

    # =========================================================
    # SAVE RESULTS
    # =========================================================

    output = {

        "model":
            OLLAMA_MODEL,

        "retrieval_top_k":
            TOP_K,

        "confidence_threshold":
            CONFIDENCE_THRESHOLD,

        "summary":
            summary,

        "tests":
            results_output

    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    # =========================================================
    # FINAL REPORT
    # =========================================================

    print("\n" + "=" * 60)
    print("RAG EVALUATION SUMMARY")
    print("=" * 60)

    print(
        f"\nTotal tests: {total_tests}"
    )

    print(
        f"Answer tests: "
        f"{answer_passed}/{answer_tests}"
    )

    print(
        f"Answer accuracy: "
        f"{answer_accuracy:.2f}%"
    )

    print(
        f"Refusal tests: "
        f"{refusal_passed}/{refusal_tests}"
    )

    print(
        f"Refusal accuracy: "
        f"{refusal_accuracy:.2f}%"
    )

    print(
        f"Overall accuracy: "
        f"{overall_accuracy:.2f}%"
    )

    print(
        f"\nResults saved to:"
        f"\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()