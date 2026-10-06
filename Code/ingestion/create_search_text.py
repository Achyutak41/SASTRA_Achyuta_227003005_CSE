import json
from pathlib import Path


INPUT_FILE = Path(
    "Input_Data/processed/EcuExtract.json"
)

OUTPUT_FILE = Path(
    "Input_Data/processed/EcuExtract_searchable.txt"
)


def create_searchable_text(data):
    """Convert structured AUTOSAR JSON into human-readable text."""

    lines = []

    lines.append("AUTOSAR ARCHITECTURE KNOWLEDGE BASE")
    lines.append("=" * 60)
    lines.append("")

    # ---------------------------------------------------------
    # Document information
    # ---------------------------------------------------------

    lines.append("DOCUMENT")
    lines.append("-" * 60)
    lines.append(f"File: {data['file_name']}")
    lines.append(f"Root Element: {data['root_element']}")
    lines.append("")

    # ---------------------------------------------------------
    # Software components
    # ---------------------------------------------------------

    lines.append("SOFTWARE COMPONENTS")
    lines.append("-" * 60)

    for component in data["software_components"]:

        lines.append(
            f"Component: {component['name']}"
        )

        lines.append(
            f"Type: {component['type']}"
        )

        for port in component["provided_ports"]:

            lines.append(
                f"Provides Port: {port['name']}"
            )

            lines.append(
                f"Provides Interface: "
                f"{port['interface_ref']}"
            )

        for port in component["required_ports"]:

            lines.append(
                f"Requires Port: {port['name']}"
            )

            lines.append(
                f"Requires Interface: "
                f"{port['interface_ref']}"
            )

        lines.append("")

    # ---------------------------------------------------------
    # Interfaces
    # ---------------------------------------------------------

    lines.append("INTERFACES")
    lines.append("-" * 60)

    for interface in data["interfaces"]:

        lines.append(
            f"Interface: {interface['name']}"
        )

        lines.append(
            f"Type: {interface['type']}"
        )

        lines.append("")

    # ---------------------------------------------------------
    # Runnables
    # ---------------------------------------------------------

    lines.append("RUNNABLE ENTITIES")
    lines.append("-" * 60)

    for runnable in data["runnables"]:

        lines.append(
            f"Runnable: {runnable}"
        )

    lines.append("")

    # ---------------------------------------------------------
    # Connectors
    # ---------------------------------------------------------

    lines.append("CONNECTORS")
    lines.append("-" * 60)

    for connector in data["connectors"]:

        lines.append(
            f"Connector: {connector['name']}"
        )

        lines.append(
            f"Type: {connector['type']}"
        )

        for reference in connector["references"]:

            lines.append(
                f"{reference['type']}: "
                f"{reference['value']}"
            )

        lines.append("")

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    lines.append("ARCHITECTURAL RELATIONSHIPS")
    lines.append("-" * 60)

    for relationship in data["relationships"]:

        relationship_type = relationship["type"]

        if relationship_type == "PROVIDES_INTERFACE":

            lines.append(
                f"{relationship['component']} "
                f"provides interface "
                f"{relationship['interface_ref']} "
                f"through port "
                f"{relationship['port']}."
            )

        elif relationship_type == "REQUIRES_INTERFACE":

            lines.append(
                f"{relationship['component']} "
                f"requires interface "
                f"{relationship['interface_ref']} "
                f"through port "
                f"{relationship['port']}."
            )

        elif relationship_type == "CONNECTOR":

            lines.append(
                f"Connector "
                f"{relationship['connector']} "
                f"({relationship['connector_type']}) "
                f"connects AUTOSAR references."
            )

            for reference in relationship["provider_ports"]:

                lines.append(
                    f"Provider port reference: "
                    f"{reference}"
                )

            for reference in relationship["required_ports"]:

                lines.append(
                    f"Required port reference: "
                    f"{reference}"
                )

            for component in relationship["context_components"]:

                lines.append(
                    f"Context component reference: "
                    f"{component}"
                )

            lines.append("")

    return "\n".join(lines)


def main():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input JSON not found: {INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    searchable_text = create_searchable_text(data)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(searchable_text)

    print("=" * 60)
    print("SEARCHABLE TEXT GENERATION")
    print("=" * 60)

    print(
        f"\nInput: {INPUT_FILE}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print(
        f"\nCharacters generated: "
        f"{len(searchable_text)}"
    )

    print("\nGeneration completed successfully.")


if __name__ == "__main__":
    main()