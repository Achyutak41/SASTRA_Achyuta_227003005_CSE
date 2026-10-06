import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict


def get_local_name(tag):
    """Remove XML namespace from an XML tag."""
    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag


def get_child_text(element, child_name):
    """Return the text of a direct child element."""

    for child in element:
        if get_local_name(child.tag) == child_name:
            if child.text:
                return child.text.strip()

    return None


def get_descendants(element, tag_name):
    """Return all descendants matching a local XML tag name."""

    matches = []

    for child in element.iter():

        if get_local_name(child.tag) == tag_name:
            matches.append(child)

    return matches


def extract_components(root):
    """Extract AUTOSAR software components."""

    components = []

    component_tags = {
        "APPLICATION-SW-COMPONENT-TYPE",
        "SERVICE-SW-COMPONENT-TYPE",
        "COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE",
    }

    for element in root.iter():

        tag = get_local_name(element.tag)

        if tag not in component_tags:
            continue

        name = get_child_text(element, "SHORT-NAME")

        if not name:
            continue

        ports = []

        for port in element.iter():

            port_type = get_local_name(port.tag)

            if port_type not in {
                "P-PORT-PROTOTYPE",
                "R-PORT-PROTOTYPE",
            }:
                continue

            port_name = get_child_text(
                port,
                "SHORT-NAME"
            )

            if port_name:

                ports.append({
                    "name": port_name,
                    "type": port_type
                })

        components.append({
            "name": name,
            "type": tag,
            "ports": ports
        })

    return components


def extract_interfaces(root):
    """Extract sender-receiver and client-server interfaces."""

    interfaces = []

    interface_tags = {
        "SENDER-RECEIVER-INTERFACE",
        "CLIENT-SERVER-INTERFACE",
    }

    for element in root.iter():

        tag = get_local_name(element.tag)

        if tag not in interface_tags:
            continue

        name = get_child_text(
            element,
            "SHORT-NAME"
        )

        if name:

            interfaces.append({
                "name": name,
                "type": tag
            })

    return interfaces


def extract_runnables(root):
    """Extract runnable entities."""

    runnables = []

    for element in root.iter():

        if get_local_name(element.tag) != "RUNNABLE-ENTITY":
            continue

        name = get_child_text(
            element,
            "SHORT-NAME"
        )

        if name:
            runnables.append(name)

    return runnables


def extract_connectors(root):
    """Extract software connectors."""

    connectors = []

    connector_tags = {
        "ASSEMBLY-SW-CONNECTOR",
        "DELEGATION-SW-CONNECTOR",
    }

    for element in root.iter():

        tag = get_local_name(element.tag)

        if tag not in connector_tags:
            continue

        name = get_child_text(
            element,
            "SHORT-NAME"
        )

        if name:
            connectors.append({
                "name": name,
                "type": tag
            })

    return connectors


def parse_arxml(file_path):

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"ARXML file not found: {file_path}"
        )

    tree = ET.parse(file_path)
    root = tree.getroot()

    data = {
        "file_name": file_path.name,
        "root_element": get_local_name(root.tag),
        "software_components": extract_components(root),
        "interfaces": extract_interfaces(root),
        "runnables": extract_runnables(root),
        "connectors": extract_connectors(root),
    }

    return data


if __name__ == "__main__":

    input_file = (
        "Input_Data/sample_hld/EcuExtract.arxml"
    )

    data = parse_arxml(input_file)

    print("=" * 60)
    print("AUTOSAR STRUCTURED PARSER")
    print("=" * 60)

    print(
        f"\nFile: {data['file_name']}"
    )

    print(
        f"Root: {data['root_element']}"
    )

    print(
        f"\nSoftware Components: "
        f"{len(data['software_components'])}"
    )

    for component in data["software_components"]:
        print(
            f"  - {component['name']} "
            f"({component['type']})"
        )

    print(
        f"\nInterfaces: "
        f"{len(data['interfaces'])}"
    )

    for interface in data["interfaces"]:
        print(
            f"  - {interface['name']} "
            f"({interface['type']})"
        )

    print(
        f"\nRunnables: "
        f"{len(data['runnables'])}"
    )

    for runnable in data["runnables"][:20]:
        print(f"  - {runnable}")

    print(
        f"\nConnectors: "
        f"{len(data['connectors'])}"
    )

    for connector in data["connectors"]:
        print(
            f"  - {connector['name']} "
            f"({connector['type']})"
        )

    print("\n" + "=" * 60)
    print("PARSING COMPLETED")
    print("=" * 60)