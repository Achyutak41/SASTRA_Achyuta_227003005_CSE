import json
import sys
import time
from pathlib import Path


# =============================================================
# PROJECT PATHS
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAG_DIR = PROJECT_ROOT / "Code" / "rag"

EVALUATION_FILE = (
    PROJECT_ROOT
    / "Evaluation_Results"
    / "comprehensive_evaluation_questions.json"
)

RESULT_FILE = (
    PROJECT_ROOT
    / "Evaluation_Results"
    / "comprehensive_evaluation_results.json"
)


# =============================================================
# IMPORT RAG PIPELINE
# =============================================================

if str(RAG_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_DIR))

from rag_pipeline import (
    answer_question,
    TOP_K
)


# =============================================================
# LOAD QUESTIONS
# =============================================================

def load_questions():

    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =============================================================
# CHECK ANSWER KEYWORDS
# =============================================================

def check_answer(
    answer,
    expected_keywords
):

    answer_lower = answer.lower()

    missing = []

    for keyword in expected_keywords:

        if keyword.lower() not in answer_lower:

            missing.append(keyword)

    return missing


# =============================================================
# CHECK REFUSAL
# =============================================================

def check_refusal(answer):

    refusal_phrases = [
        "does not contain sufficient evidence",
        "insufficient evidence",
        "not contain sufficient",
        "cannot answer",
        "unable to answer"
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

    print("=" * 70)
    print("COMPREHENSIVE AUTOSAR RAG EVALUATION")
    print("=" * 70)

    questions = load_questions()

    print(
        f"\nEvaluation questions: "
        f"{len(questions)}"
    )

    print(
        "\nLoading RAG system..."
    )

    # Import retrieval loader here
    retrieval_dir = (
        PROJECT_ROOT
        / "Code"
        / "retrieval"
    )

    if str(retrieval_dir) not in sys.path:
        sys.path.insert(
            0,
            str(retrieval_dir)
        )

    from search import load_retriever

    model, index, metadata = (
        load_retriever()
    )

    print(
        f"Indexed chunks: "
        f"{index.ntotal}"
    )

    results = []

    answer_passes = 0
    answer_total = 0

    refusal_passes = 0
    refusal_total = 0

    retrieval_passes = 0

    total_time = 0.0

    # =========================================================
    # RUN TESTS
    # =========================================================

    for item in questions:

        question_id = item["id"]
        question = item["question"]

        expected_keywords = (
            item["expected_keywords"]
        )

        expected_behavior = (
            item["expected_behavior"]
        )

        print(
            f"\n[{question_id}] "
            f"{question}"
        )

        start_time = time.perf_counter()

        try:

            result = answer_question(
                question,
                model,
                index,
                metadata,
                top_k=TOP_K
            )

            elapsed = (
                time.perf_counter()
                - start_time
            )

            total_time += elapsed

            answer = result["answer"]

            confidence = (
                result["confidence"]
            )

            sufficient = (
                result["evidence_sufficient"]
            )

            retrieved_text = " ".join(
                r["text"]
                for r in result["results"]
            )

            # -------------------------------------------------
            # SUPPORTED QUESTION
            # -------------------------------------------------

            if expected_behavior == "answer":

                answer_total += 1

                missing = check_answer(
                    answer,
                    expected_keywords
                )

                answer_pass = (
                    len(missing) == 0
                )

                if answer_pass:
                    answer_passes += 1

                # Retrieval evaluation
                retrieval_missing = (
                    check_answer(
                        retrieved_text,
                        expected_keywords
                    )
                )

                retrieval_pass = (
                    len(retrieval_missing) == 0
                )

                if retrieval_pass:
                    retrieval_passes += 1

                status = (
                    "PASS"
                    if answer_pass
                    else "FAIL"
                )

            # -------------------------------------------------
            # UNSUPPORTED QUESTION
            # -------------------------------------------------

            else:

                refusal_total += 1

                refusal_pass = (
                    check_refusal(answer)
                )

                if refusal_pass:
                    refusal_passes += 1

                missing = []

                retrieval_pass = True

                status = (
                    "PASS"
                    if refusal_pass
                    else "FAIL"
                )

            # -------------------------------------------------
            # TOP SCORE
            # -------------------------------------------------

            if result["results"]:

                top_score = (
                    result["results"][0]
                    ["final_score"]
                )

            else:

                top_score = 0.0

            print(
                f"  Status: {status}"
            )

            print(
                f"  Confidence: "
                f"{confidence}"
            )

            print(
                f"  Top score: "
                f"{top_score:.4f}"
            )

            print(
                f"  Time: "
                f"{elapsed:.2f}s"
            )

            results.append(
                {
                    "id": question_id,
                    "question": question,
                    "expected_behavior":
                        expected_behavior,
                    "expected_keywords":
                        expected_keywords,
                    "answer": answer,
                    "confidence": confidence,
                    "evidence_sufficient":
                        sufficient,
                    "top_score":
                        round(top_score, 4),
                    "response_time_seconds":
                        round(elapsed, 4),
                    "status": status,
                    "missing_keywords":
                        missing
                }
            )

        except Exception as error:

            print(
                f"  ERROR: {error}"
            )

            results.append(
                {
                    "id": question_id,
                    "question": question,
                    "status": "ERROR",
                    "error": str(error)
                }
            )

    # =========================================================
    # METRICS
    # =========================================================

    total_tests = len(questions)

    passed_tests = sum(
        1
        for result in results
        if result.get("status") == "PASS"
    )

    overall_accuracy = (
        passed_tests / total_tests * 100
        if total_tests
        else 0
    )

    answer_accuracy = (
        answer_passes / answer_total * 100
        if answer_total
        else 0
    )

    refusal_accuracy = (
        refusal_passes / refusal_total * 100
        if refusal_total
        else 0
    )

    retrieval_accuracy = (
        retrieval_passes / answer_total * 100
        if answer_total
        else 0
    )

    average_response_time = (
        total_time / total_tests
        if total_tests
        else 0
    )

    # =========================================================
    # SUMMARY
    # =========================================================

    summary = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": (
            total_tests - passed_tests
        ),
        "overall_accuracy_percent":
            round(overall_accuracy, 2),
        "supported_questions":
            answer_total,
        "supported_answer_accuracy_percent":
            round(answer_accuracy, 2),
        "unsupported_questions":
            refusal_total,
        "refusal_accuracy_percent":
            round(refusal_accuracy, 2),
        "retrieval_accuracy_percent":
            round(retrieval_accuracy, 2),
        "average_response_time_seconds":
            round(average_response_time, 4)
    }

    output = {
        "summary": summary,
        "results": results
    }

    # =========================================================
    # SAVE RESULTS
    # =========================================================

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2
        )

    # =========================================================
    # PRINT FINAL RESULTS
    # =========================================================

    print("\n")
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Total tests: "
        f"{total_tests}"
    )

    print(
        f"Passed: "
        f"{passed_tests}"
    )

    print(
        f"Failed: "
        f"{total_tests - passed_tests}"
    )

    print(
        f"Overall accuracy: "
        f"{overall_accuracy:.2f}%"
    )

    print(
        f"Supported answer accuracy: "
        f"{answer_accuracy:.2f}%"
    )

    print(
        f"Refusal accuracy: "
        f"{refusal_accuracy:.2f}%"
    )

    print(
        f"Retrieval accuracy: "
        f"{retrieval_accuracy:.2f}%"
    )

    print(
        f"Average response time: "
        f"{average_response_time:.2f}s"
    )

    print(
        f"\nResults saved to:"
        f"\n{RESULT_FILE}"
    )


if __name__ == "__main__":
    main()