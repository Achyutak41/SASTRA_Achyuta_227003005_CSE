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

The AUTOSAR ARXML example files are obtained from the public
`patrikja/autosar` GitHub repository.

The ARXML directory contains a license permitting redistribution
and use in source and binary forms, subject to the conditions
specified in the repository's `ARXML/LICENSE` file.

The original copyright notice and license conditions will be
retained and cited in the project documentation.

License file:

https://github.com/patrikja/autosar/blob/master/ARXML/LICENSE

Source repository:

https://github.com/patrikja/autosar   
    

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
    
      
## Input Documents

### 1. EcuExtract.arxml
* **Document ID:** `AUTOSAR_001`
* **File:** `EcuExtract.arxml`
* **Document Type:** AUTOSAR 4.x ARXML
* **Purpose:** This file is used as the primary AUTOSAR architecture knowledge source for the project. It contains structured AUTOSAR information including:
  * Application software components
  * Service software components
  * Ports
  * Provided interfaces
  * Required interfaces
  * Data elements
  * Runnable entities
  * Software compositions
  * Component prototypes
  * Connectors
  * System mappings
  * System signals
  * ECU-related information
* **Source Repository:** [patrikja/autosar](https://github.com/patrikja/autosar)
* **Source File:** [EcuExtract.arxml on GitHub](https://github.com/patrikja/autosar/blob/master/ARXML/EcuExtract.arxml)
* **License:** The ARXML directory provides a BSD-style license. The applicable copyright notice, conditions, and disclaimer will be retained with the project documentation.
* **License File:** [LICENSE on GitHub](https://github.com/patrikja/autosar/blob/master/ARXML/LICENSE)
* **Usage in this Project:** The file will be used for academic development and evaluation of the AI-powered AUTOSAR HLD Document Analysis Assistant. The data will be parsed and converted into a searchable knowledge representation for later retrieval and RAG experiments.

---

### ⚠️ Important: Technical Nomenclature
A critical technical distinction must be maintained throughout the project: **`EcuExtract.arxml` is not an HLD PDF.** 

It is an **AUTOSAR ARXML architecture description**. Accordingly, the project accurately describes this knowledge base as an **AUTOSAR HLD / Architecture Knowledge Base** rather than treating the ARXML as a conventional, unstructured text document. This distinction allows the RAG pipeline to exploit structured AUTOSAR relationships rather than processing it as plain text.

---

### 🔍 File Verification & Validation
Before committing changes, open `EcuExtract.arxml` and verify that it contains the following baseline architecture entities:

```text
- Door
- DoorControl
- DoorStatus
- DoorCommands
- CombinedStatus
- EDC
- Ports
- Interfaces
- Runnable entities
- Connectors
- System mappings
```

