# Checkpoint 2 — AUTOSAR ARXML Processing Pipeline

## Objective
Convert `Input_Data/sample_hld/EcuExtract.arxml` into a structured, searchable knowledge representation for downstream RAG consumption.

## Processing Pipeline
Transforms `EcuExtract.arxml` via an XML parser into structured AUTOSAR components (Software Components, Ports, Interfaces, Runnables, Connectors, Relationships) to generate `EcuExtract.json` and `EcuExtract_searchable.txt`.

## Extracted Architecture Information

### Metric Summary

| Element | Count |
| :--- | :--- |
| **Software Components** | 3 |
| **Interfaces** | 4 |
| **Runnable Entities** | 4 |
| **Connectors** | 6 |
| **Relationships** | 15 |

### Breakdown Highlights
* **Software Components:** `Door`, `IoHwAb`, `DoorControl`
* **Interfaces:** `DigitalServiceWrite`, `DoorStatus`, `DoorCommands`, `CombinedStatus`
* **Runnable Entities:** `DoorMain`, `SetLocked`, `DigitalWrite`, `Main`
* **Connectors:** Includes `DoorLeft_Command_to_Control_CommandsLeft`, `DoorRight_Command_to_Control_CommandsRight`, and 4 additional topological connectors.

## Generated Artifacts
Outputs are located under the `processed` data directory:
* `Input_Data/processed/EcuExtract.json`
* `Input_Data/processed/EcuExtract_searchable.txt` (~6,026 characters indexing metadata, ports, interfaces, and topologies).

## Architecture Design Decisions
📌 **Preservation of Raw Reference Paths:** Raw AUTOSAR reference paths (e.g., `/Demo/Interfaces/DoorStatus`) are intentionally preserved to ensure traceability and strict data integrity without unsupported composition-instance assumptions.

## Current Status
* **Status:** **`COMPLETE`**
* **Next Steps:** Ready as a verified baseline dataset for the retrieval and chunking stage.
