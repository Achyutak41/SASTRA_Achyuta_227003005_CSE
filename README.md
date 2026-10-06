# AI-Powered AUTOSAR HLD Document Analysis Assistant

## Project Overview

The AI-Powered AUTOSAR HLD Document Analysis Assistant is an AI-based engineering support system designed to help engineers analyze and retrieve information from AUTOSAR High-Level Design (HLD) documents.

The system will use Retrieval-Augmented Generation (RAG) to provide grounded answers based on approved HLD documents, along with source/page citations.

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
├── Input_Data/
├── Code/
├── Model_Prompts_Config/
├── Evaluation_Results/
├── Documentation/
├── Video/
├── Declarations/
├── README.md
├── requirements.txt
└── .gitignore
# AUTOSAR HLD Knowledge Base

## Purpose

This directory contains the AUTOSAR High-Level Design (HLD) documents
used as the knowledge base for the AI-powered AUTOSAR HLD Document
Analysis Assistant.

## Intended Use

The documents will be used for:

- Document understanding
- Semantic retrieval
- Retrieval-Augmented Generation (RAG)
- Architecture question answering
- Component identification
- Interface identification
- Dependency analysis
- Grounded response generation
- Citation testing

## Required HLD Information

The documents should contain, where available:

- Software components
- Interfaces
- Ports
- Signals
- Dependencies
- Functional flows
- Architecture descriptions
- Integration information

## Data Source

To be documented for every document added.

## License / Permission

To be documented for every document added.

## Number of Documents

Currently: 0

## Status

Checkpoint 1 - Dataset preparation