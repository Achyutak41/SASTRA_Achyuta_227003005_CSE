# AUTOSAR HLD Knowledge Base

## Project
**AI-Powered AUTOSAR HLD Document Analysis Assistant**

This directory contains the public AUTOSAR architecture example files that will be used as the initial knowledge base for the project. 

The data will later be processed and indexed for Retrieval-Augmented Generation (RAG), semantic search, architecture analysis, and grounded question answering.

---

## Purpose
The purpose of this knowledge base is to provide AUTOSAR-related architecture information for developing and evaluating the AI-powered HLD analysis assistant.

The files will be used to investigate and retrieve information such as:
- Software components
- Ports
- Interfaces
- Data elements
- Signals
- Runnables
- Component references
- Software compositions
- ECU-related information
- Architecture relationships
- Dependencies

---

## Input Documents

### 1. EcuExtract.arxml
- **File:** `EcuExtract.arxml`
- **Document Type:** AUTOSAR ARXML
- **Purpose:** Used as the primary AUTOSAR architecture example for extracting software components, ports, interfaces, data elements, signals, component references, and related architecture information.
- **Source:** GitHub - patrikja/autosar
- **Source URL:** [EcuExtract.arxml on GitHub](https://github.com/patrikja/autosar/blob/master/ARXML/EcuExtract.arxml)

### 2. SimpleExample.xml
- **File:** `SimpleExample.xml`
- **Document Type:** AUTOSAR XML example
- **Purpose:** Used as a simpler AUTOSAR architecture example for initial parsing, testing, retrieval, and question-answering experiments. The file provides a smaller example that can be useful during the early development and debugging stages of the RAG pipeline.
- **Source:** GitHub - patrikja/autosar
- **Source URL:** [SimpleExample.xml on GitHub](https://github.com/patrikja/autosar/blob/master/oldARSim/SimpleExample.xml)

---

## Data Source
The initial dataset consists of publicly accessible AUTOSAR example files obtained from the patrikja/autosar GitHub repository. The original source and applicable licensing information will be recorded in the project dataset inventory.

## License / Permission
The files are obtained from a public GitHub repository. The applicable repository/file license must be reviewed and retained with the project documentation before redistribution or publication.

**Note:** No confidential or proprietary automotive company documents are intentionally included in this knowledge base.

---

## Data Processing Plan
The input files will later pass through the following pipeline:

```text
AUTOSAR XML / ARXML
        │
        ▼
Document Parsing
        │
        ▼
Element / Structure Extraction
        │
        ▼
Text Representation + Metadata
        │
        ▼
Chunking
        │
        ▼
Embedding Generation
        │
        ▼
Vector Database
        │
        ▼
Semantic Retrieval
        │
        ▼
LLM / RAG
        │
        ▼
Grounded Response + Source Citation
```

---

## Intended Use in the Project
The knowledge base will support:
1. AUTOSAR document understanding
2. Architecture information retrieval
3. Semantic search
4. RAG-based question answering
5. Software component identification
6. Interface identification
7. Port identification
8. Dependency analysis
9. Architecture relationship analysis
10. Grounded response generation
11. Citation and retrieval evaluation

---

## Dataset Inventory
The complete metadata for each input file is maintained separately in: `Input_Data/dataset_inventory.csv`

The inventory will contain:
- Document ID
- Document name
- Source
- Document type
- License/permission
- Purpose
- Status

### Current Dataset Status

| Document | Status |
| :--- | :--- |
| `EcuExtract.arxml` | Added |
| `SimpleExample.xml` | Added |

**Total Documents:** 2
