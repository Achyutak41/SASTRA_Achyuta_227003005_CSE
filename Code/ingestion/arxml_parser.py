import xml.etree.ElementTree as ET
from pathlib import Path


def get_local_name(tag):
    """Remove XML namespace from an XML tag."""
    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag


def get_child_text(element, child_name):
    """Return the text of the first matching descendant element."""

    for child in element.iter():

        if get_local_name(child.tag) == child_name:

            if child.text:
                return child.text.strip()

    return None


def get_reference(element, reference_tags):
    """Return the first matching AUTOSAR reference."""

    for child in element.iter():

        tag = get_local_name(child.tag)

        if tag in reference_tags:

            if child.text:
                return child.text.strip()

    return None


def extract_components(root):
    """Extract AUTOSAR software components with their ports."""

    components = []

    component_tags = {
        "APPLICATION-SW-COMPONENT-TYPE",
        "SERVICE-SW-COMPONENT-TYPE",
        "COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE",
    }

    port_tags = {
        "P-PORT-PROTOTYPE",
        "R-PORT-PROTOTYPE",
    }

    for element in root.iter():

        tag = get_local_name(element.tag)

        if tag not in component_tags:
            continue

        name = get_child_text(
            element,
            "SHORT-NAME"
        )

        if not name:
            continue

        provided_ports = []
        required_ports = []

        for port in element.iter():

            port_type = get_local_name(port.tag)

            if port_type not in port_tags:
                continue

            port_name = get_child_text(
                port,
                "SHORT-NAME"
            )

            if not port_name:
                continue

            interface_ref = get_reference(
                port,
                {
                    "TARGET-P-PORT-PROTOTYPE-REF",
                    "TARGET-R-PORT-PROTOTYPE-REF",
                    "PROVIDED-INTERFACE-TREF",
                    "REQUIRED-INTERFACE-TREF",
                }
            )

            port_data = {
                "name": port_name,
                "type": port_type,
                "interface_ref": interface_ref
            }

            if port_type == "P-PORT-PROTOTYPE":

                provided_ports.append(port_data)

            elif port_type == "R-PORT-PROTOTYPE":

                required_ports.append(port_data)

        components.append({
            "name": name,
            "type": tag,
            "provided_ports": provided_ports,
            "required_ports": required_ports
        })

    return components


def extract_interfaces(root):
    """Extract AUTOSAR interfaces."""

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

        if not name:
            continue

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
    """Extract AUTOSAR software connectors."""

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

        if not name:
            continue

        connector_data = {
            "name": name,
            "type": tag,
            "references": []
        }

        # Collect reference elements inside the connector.
        for child in element.iter():

            child_tag = get_local_name(child.tag)

            if child_tag.endswith("-REF"):

                if child.text:

                    connector_data["references"].append({
                        "type": child_tag,
                        "value": child.text.strip()
                    })

        connectors.append(connector_data)

    return connectors

def extract_relationships(data):
    """Build normalized relationships between components, ports and interfaces."""

    relationships = []

    # ---------------------------------------------------------
    # Component -> Port -> Interface relationships
    # ---------------------------------------------------------

    for component in data["software_components"]:

        component_name = component["name"]

        for port in component["provided_ports"]:

            relationships.append({
                "type": "PROVIDES_INTERFACE",
                "component": component_name,
                "port": port["name"],
                "interface_ref": port["interface_ref"]
            })

        for port in component["required_ports"]:

            relationships.append({
                "type": "REQUIRES_INTERFACE",
                "component": component_name,
                "port": port["name"],
                "interface_ref": port["interface_ref"]
            })

    # ---------------------------------------------------------
    # Connector relationships
    # ---------------------------------------------------------

    for connector in data["connectors"]:

        references = connector["references"]

        context_components = []
        provider_ports = []
        required_ports = []

        for reference in references:

            ref_type = reference["type"]
            ref_value = reference["value"]

            if ref_type == "CONTEXT-COMPONENT-REF":

                context_components.append(ref_value)

            elif ref_type == "TARGET-P-PORT-REF":

                provider_ports.append(ref_value)

            elif ref_type == "TARGET-R-PORT-REF":

                required_ports.append(ref_value)

        relationships.append({
            "type": "CONNECTOR",
            "connector": connector["name"],
            "connector_type": connector["type"],
            "context_components": context_components,
            "provider_ports": provider_ports,
            "required_ports": required_ports
        })

    return relationships


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

    "root_element":
        get_local_name(root.tag),

    "software_components":
        extract_components(root),

    "interfaces":
        extract_interfaces(root),

    "runnables":
        extract_runnables(root),

    "connectors":
        extract_connectors(root)
}

    data["relationships"] = extract_relationships(data)


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
            f"\n  - {component['name']} "
            f"({component['type']})"
        )

        print(
            f"    Provided Ports: "
            f"{len(component['provided_ports'])}"
        )

        for port in component["provided_ports"]:

            print(
                f"      P: {port['name']} "
                f"-> {port['interface_ref']}"
            )

        print(
            f"    Required Ports: "
            f"{len(component['required_ports'])}"
        )

        for port in component["required_ports"]:

            print(
                f"      R: {port['name']} "
                f"-> {port['interface_ref']}"
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

    for runnable in data["runnables"]:

        print(
            f"  - {runnable}"
        )

    print(
        f"\nConnectors: "
        f"{len(data['connectors'])}"
    )

    for connector in data["connectors"]:

        print(
            f"\n  - {connector['name']} "
            f"({connector['type']})"
        )

        for reference in connector["references"]:

            print(
                f"      {reference['type']}: "
                f"{reference['value']}"
            )

    print("\n" + "=" * 60)
    print("PARSING COMPLETED")
    print("=" * 60)