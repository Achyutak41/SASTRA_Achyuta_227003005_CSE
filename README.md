# AI-Powered AUTOSAR HLD Document Analysis Assistant

## Project Overview

The AI-Powered AUTOSAR HLD Document Analysis Assistant is an AI-based
engineering support system designed to help engineers analyze and
retrieve information from AUTOSAR High-Level Design (HLD) documents.

The system will use Retrieval-Augmented Generation (RAG) to provide
grounded answers based on approved HLD documents, along with
source/page citations.

## Objectives

- Analyze AUTOSAR HLD documents
- Extract relevant architectural information
- Provide natural-language question answering
- Retrieve relevant HLD sections using semantic search
- Generate grounded responses using an LLM
- Provide page/section citations
- Support architecture analysis and knowledge reuse
- Assist engineers without replacing human engineering decisions

## Planned Technologies

- Python
- Large Language Model (LLM)
- Retrieval-Augmented Generation (RAG)
- Embedding Model
- FAISS / ChromaDB
- Streamlit
- FastAPI / Flask
- Docker

## Project Structure

```text
SASTRA_Achyuta_227003005_CSE/
│
├── Synopsis/
│
├── Input_Data/
│   ├── sample_hld/
│   │   └── README.md
│   └── dataset_inventory.csv
│
├── Code/
│
├── Model_Prompts_Config/
│
├── Evaluation_Results/
│
├── Documentation/
│
├── Video/
│
├── Declarations/
│
├── README.md
├── requirements.txt
└── .gitignore