import json
from pathlib import Path


INPUT_FILE = Path(
    "Input_Data/processed/EcuExtract.json"
)

OUTPUT_FILE = Path(
    "Input_Data/processed/EcuExtract_chunks.json"
)


def create_chunks(data):
    """Create meaningful AUTOSAR architecture chunks."""

    chunks = []
    chunk_id = 1

    # =========================================================
    # 1. DOCUMENT CHUNK
    # =========================================================

    chunks.append({
        "chunk_id": f"chunk_{chunk_id:03d}",
        "chunk_type": "document",
        "text": (
            f"AUTOSAR document {data['file_name']} "
            f"has root element {data['root_element']}."
        ),
        "source": data["file_name"]
    })

    chunk_id += 1

    # =========================================================
    # 2. SOFTWARE COMPONENT CHUNKS
    # =========================================================

    for component in data["software_components"]:

        lines = [
            f"Software component: {component['name']}.",
            f"Component type: {component['type']}."
        ]

        # -----------------------------------------------------
        # Provided ports
        # -----------------------------------------------------

        for port in component["provided_ports"]:

            lines.append(
                f"It provides port {port['name']} "
                f"through interface reference "
                f"{port['interface_ref']}."
            )

        # -----------------------------------------------------
        # Required ports
        # -----------------------------------------------------

        for port in component["required_ports"]:

            lines.append(
                f"It requires port {port['name']} "
                f"through interface reference "
                f"{port['interface_ref']}."
            )

        chunks.append({
            "chunk_id": f"chunk_{chunk_id:03d}",
            "chunk_type": "software_component",
            "component": component["name"],
            "text": " ".join(lines),
            "source": data["file_name"]
        })

        chunk_id += 1

    # =========================================================
    # 3. INTERFACE CHUNKS
    # =========================================================

    for interface in data["interfaces"]:

        chunks.append({
            "chunk_id": f"chunk_{chunk_id:03d}",
            "chunk_type": "interface",
            "interface": interface["name"],
            "text": (
                f"Interface {interface['name']} "
                f"is a {interface['type']}."
            ),
            "source": data["file_name"]
        })

        chunk_id += 1

    # =========================================================
    # 4. RUNNABLE ENTITY SUMMARY
    # =========================================================

    if data["runnables"]:

        runnable_names = ", ".join(
            data["runnables"]
        )

        chunks.append({
            "chunk_id": f"chunk_{chunk_id:03d}",
            "chunk_type": "runnable_summary",
            "text": (
                "The AUTOSAR architecture contains "
                "the following runnable entities: "
                f"{runnable_names}."
            ),
            "source": data["file_name"]
        })

        chunk_id += 1

    # =========================================================
    # 5. CONNECTOR CHUNKS
    # =========================================================

    for connector in data["connectors"]:

        lines = [
            f"Connector: {connector['name']}.",
            f"Connector type: {connector['type']}."
        ]

        for reference in connector["references"]:

            lines.append(
                f"{reference['type']}: "
                f"{reference['value']}."
            )

        chunks.append({
            "chunk_id": f"chunk_{chunk_id:03d}",
            "chunk_type": "connector",
            "connector": connector["name"],
            "text": " ".join(lines),
            "source": data["file_name"]
        })

        chunk_id += 1

    # =========================================================
    # 6. ARCHITECTURAL RELATIONSHIP CHUNKS
    # =========================================================

    for relationship in data["relationships"]:

        relationship_type = relationship["type"]

        # -----------------------------------------------------
        # PROVIDES_INTERFACE
        # -----------------------------------------------------

        if relationship_type == "PROVIDES_INTERFACE":

            text = (
                f"The software component "
                f"{relationship['component']} "
                f"PROVIDES the interface "
                f"{relationship['interface_ref']} "
                f"through its provided port "
                f"{relationship['port']}. "
                f"This is a PROVIDES_INTERFACE relationship."
            )

        # -----------------------------------------------------
        # REQUIRES_INTERFACE
        # -----------------------------------------------------

        elif relationship_type == "REQUIRES_INTERFACE":

            text = (
                f"The software component "
                f"{relationship['component']} "
                f"REQUIRES the interface "
                f"{relationship['interface_ref']} "
                f"through its required port "
                f"{relationship['port']}. "
                f"This is a REQUIRES_INTERFACE relationship."
            )

        # -----------------------------------------------------
        # CONNECTOR
        # -----------------------------------------------------

        elif relationship_type == "CONNECTOR":

            text = (
                f"Connector {relationship['connector']} "
                f"is a {relationship['connector_type']}. "
            )

            # Provider references
            if relationship["provider_ports"]:

                text += (
                    "Provider port references: "
                    + ", ".join(
                        relationship["provider_ports"]
                    )
                    + ". "
                )

            # Required references
            if relationship["required_ports"]:

                text += (
                    "Required port references: "
                    + ", ".join(
                        relationship["required_ports"]
                    )
                    + ". "
                )

            # Context component references
            if relationship["context_components"]:

                text += (
                    "Context component references: "
                    + ", ".join(
                        relationship["context_components"]
                    )
                    + "."
                )

        else:
            continue

        chunks.append({
            "chunk_id": f"chunk_{chunk_id:03d}",
            "chunk_type": "relationship",
            "relationship_type": relationship_type,
            "text": text,
            "source": data["file_name"]
        })

        chunk_id += 1

    # =========================================================
    # 7. INTERFACE PROVIDER SUMMARIES
    #
    # IMPORTANT:
    # This section is intentionally OUTSIDE the relationship
    # loop so that provider summaries are created only once.
    # =========================================================

    interface_providers = {}

    for relationship in data["relationships"]:

        if relationship["type"] != "PROVIDES_INTERFACE":
            continue

        interface_ref = relationship["interface_ref"]

        # Extract interface name from AUTOSAR reference
        interface_name = interface_ref.split("/")[-1]

        if interface_name not in interface_providers:

            interface_providers[interface_name] = []

        provider_description = (
            f"{relationship['component']} "
            f"through port {relationship['port']}"
        )

        # -----------------------------------------------------
        # Prevent duplicate provider entries
        # -----------------------------------------------------

        if provider_description not in interface_providers[
            interface_name
        ]:

            interface_providers[interface_name].append(
                provider_description
            )

    # ---------------------------------------------------------
    # Create one summary chunk for each interface
    # ---------------------------------------------------------

    for interface_name, providers in interface_providers.items():

        provider_text = ", ".join(providers)

        chunks.append({
            "chunk_id": f"chunk_{chunk_id:03d}",
            "chunk_type": "interface_provider_summary",
            "interface": interface_name,
            "text": (
                f"The AUTOSAR interface {interface_name} "
                f"is PROVIDED by {provider_text}."
            ),
            "source": data["file_name"]
        })

        chunk_id += 1

    # =========================================================
    # RETURN ALL CHUNKS
    # =========================================================

    return chunks


def main():

    # =========================================================
    # Check input file
    # =========================================================

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    # =========================================================
    # Load parsed AUTOSAR JSON
    # =========================================================

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    # =========================================================
    # Create chunks
    # =========================================================

    chunks = create_chunks(data)

    # =========================================================
    # Ensure output directory exists
    # =========================================================

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # =========================================================
    # Save chunks
    # =========================================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    # =========================================================
    # Display generation results
    # =========================================================

    print("=" * 60)
    print("AUTOSAR SEMANTIC CHUNK GENERATION")
    print("=" * 60)

    print(f"\nInput: {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")

    print(f"\nChunks generated: {len(chunks)}")

    # =========================================================
    # Count chunk types
    # =========================================================

    print("\nChunk types:")

    counts = {}

    for chunk in chunks:

        chunk_type = chunk["chunk_type"]

        counts[chunk_type] = (
            counts.get(chunk_type, 0) + 1
        )

    for chunk_type, count in counts.items():

        print(
            f"  - {chunk_type}: {count}"
        )

    print("\nGeneration completed successfully.")


if __name__ == "__main__":
    main()