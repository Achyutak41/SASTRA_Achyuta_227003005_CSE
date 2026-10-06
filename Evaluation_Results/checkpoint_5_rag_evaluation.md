# Checkpoint 5: RAG Evaluation

## Objective

The objective of this checkpoint is to evaluate the complete
AUTOSAR RAG pipeline, including retrieval, grounded answer
generation, and insufficient-evidence handling.

## Evaluation Setup

Generation model:

mistral:latest

Runtime:

Ollama

Retrieval:

FAISS with architecture-aware AUTOSAR chunks

Embedding model:

all-MiniLM-L6-v2

Evaluation questions:

6

Known-answer questions:

4

Unsupported questions:

2

## Results

| Metric | Result |
|---|---:|
| Total tests | 6 |
| Known-answer tests passed | 4/4 |
| Answer accuracy | 100.00% |
| Unsupported-question tests passed | 2/2 |
| Refusal accuracy | 100.00% |
| Overall evaluation accuracy | 100.00% |

## Individual Results

### Q1

Question:

Which component provides DigitalServiceWrite?

Result:

PASS

Generated answer correctly identified IoHwAb as the provider
of DigitalServiceWrite through Digital_Led.

Confidence:

HIGH

### Q2

Question:

Which interface does DoorControl require through StatusLeft?

Result:

PASS

Generated answer correctly identified:

/Demo/Interfaces/DoorStatus

Confidence:

HIGH

### Q3

Question:

What interfaces does the Door component provide?

Result:

PASS

Generated answer identified the expected interfaces.

Result:

PASS

Confidence:

HIGH

### Q4

Question:

What runnable entities are present in the architecture?

Result:

PASS

The generated answer identified:

- DoorMain
- SetLocked
- DigitalWrite
- Main

Confidence:

MEDIUM

### Q5

Question:

What is the maximum CPU frequency of the ECU?

Result:

PASS

The system correctly refused to provide an unsupported answer.

Confidence:

LOW

### Q6

Question:

What is the battery capacity of the vehicle?

Result:

PASS

The system correctly refused to provide an unsupported answer.

Confidence:

LOW

## Grounding Evaluation

The four supported questions were answered using retrieved
AUTOSAR evidence.

The two unsupported questions resulted in an
insufficient-evidence response.

This demonstrates the intended grounding behavior of the RAG
pipeline.

## Evaluation Method

For supported questions, answer correctness was evaluated using
expected keyword matching against the generated answer.

For unsupported questions, refusal behavior was evaluated by
checking whether the system returned an insufficient-evidence
response.

## Limitations

The evaluation dataset contains only six questions.

The answer evaluation uses keyword matching and therefore does
not constitute a complete semantic evaluation of answer quality.

The HIGH, MEDIUM, and LOW confidence labels are heuristic
retrieval-based categories and are not calibrated probability
estimates.

A larger evaluation dataset should be used for more reliable
performance measurement.

## Conclusion

The complete local AUTOSAR RAG pipeline achieved 100.00% accuracy
on the six-question evaluation set.

The system successfully answered supported AUTOSAR architecture
questions and correctly refused unsupported technical questions.