# Checkpoint 3: Semantic Retrieval Evaluation

## Objective

The objective of this checkpoint is to implement and evaluate
semantic retrieval over the processed AUTOSAR architecture knowledge base.

The retrieval pipeline uses:

1. Architecture-aware text chunks
2. Sentence-transformer embeddings
3. FAISS vector similarity search
4. Intent-aware reranking
5. Metadata mapping from retrieved vectors to source chunks

## Embedding Model

Model:

all-MiniLM-L6-v2

Embedding dimension:

384

## Vector Database

FAISS

Index type:

IndexFlatIP

The embeddings are normalized before similarity search.

## Evaluation Dataset

Five representative AUTOSAR architecture questions were evaluated.

| No. | Query | Result |
|---|---|---|
| 1 | Which interface does DoorControl require through StatusLeft? | PASS |
| 2 | What interfaces does DoorControl require? | PASS |
| 3 | What interfaces does the Door component provide? | PASS |
| 4 | Which component provides DigitalServiceWrite? | PASS |
| 5 | What runnable entities are present in the architecture? | PASS |

## Results

Queries tested: 5

Passed: 5

Failed: 0

Top-1 keyword success: 100.00%

## Representative Retrieval Results

### Query 1

Question:

Which interface does DoorControl require through StatusLeft?

Retrieved relationship:

DoorControl REQUIRES the interface
/Demo/Interfaces/DoorStatus through its required port StatusLeft.

Result:

PASS

### Query 2

Question:

What interfaces does DoorControl require?

Retrieved relationship:

DoorControl REQUIRES the interface
/Demo/Interfaces/DoorCommands through its required port CommandsLeft.

Result:

PASS

### Query 3

Question:

What interfaces does the Door component provide?

Retrieved relationship:

Door PROVIDES the interface
/Demo/Interfaces/DoorStatus through its provided port Status.

Result:

PASS

### Query 4

Question:

Which component provides DigitalServiceWrite?

Retrieved relationship:

IoHwAb PROVIDES the interface
/Demo/Services/IoHwAb/DigitalServiceWrite through its provided port Digital_Led.

Result:

PASS

### Query 5

Question:

What runnable entities are present in the architecture?

Retrieved summary:

DoorMain, SetLocked, DigitalWrite, Main.

Result:

PASS

## Evaluation Metric

Top-1 keyword success was used as the initial retrieval evaluation metric.

The retrieved top-ranked chunk was considered successful when
all expected keywords for the query were present in the retrieved
chunk text.

## Conclusion

The retrieval system achieved 100% Top-1 keyword success on the
five-query evaluation set.

The results demonstrate that the architecture-aware chunking and
intent-aware reranking strategy can retrieve relevant AUTOSAR
architecture information for representative component, interface,
relationship, and runnable-entity questions.

This evaluation is limited to five manually designed queries and
does not represent comprehensive AUTOSAR retrieval performance.
A larger evaluation set should be used in later stages.