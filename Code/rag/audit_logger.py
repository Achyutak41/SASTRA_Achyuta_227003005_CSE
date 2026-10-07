import json
from datetime import datetime
from pathlib import Path


# =============================================================
# PROJECT PATH
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = (
    PROJECT_ROOT
    / "Evaluation_Results"
    / "audit_logs"
)

LOG_FILE = (
    LOG_DIR
    / "rag_audit_log.jsonl"
)


# =============================================================
# CREATE LOG DIRECTORY
# =============================================================

def initialize_audit_log():

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


# =============================================================
# WRITE AUDIT EVENT
# =============================================================

def log_query(
    question,
    answer,
    confidence,
    evidence_sufficient,
    citations
):

    initialize_audit_log()

    event = {
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "question": question,
        "answer": answer,
        "confidence": confidence,
        "evidence_sufficient":
            evidence_sufficient,
        "citations": [
            {
                "chunk_id":
                    citation["chunk_id"],
                "source":
                    citation["source"],
                "chunk_type":
                    citation["chunk_type"]
            }
            for citation in citations
        ]
    }

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(
                event,
                ensure_ascii=False
            )
        )

        file.write("\n")


# =============================================================
# READ AUDIT LOG
# =============================================================

def read_audit_log():

    initialize_audit_log()

    if not LOG_FILE.exists():
        return []

    events = []

    with open(
        LOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            events.append(
                json.loads(line)
            )

    return events


# =============================================================
# STANDALONE TEST
# =============================================================

if __name__ == "__main__":

    log_query(
        question="Test audit question",
        answer="Test answer",
        confidence="HIGH",
        evidence_sufficient=True,
        citations=[]
    )

    print(
        f"Audit log created at:\n{LOG_FILE}"
    )