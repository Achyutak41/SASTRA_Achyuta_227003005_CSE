import xml.etree.ElementTree as ET
from pathlib import Path


def get_local_name(tag):
    """
    Remove XML namespace from an element tag.

    Example:
    {http://autosar.org/schema/r4.0}SHORT-NAME
    becomes:
    SHORT-NAME
    """
    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag


def parse_arxml(file_path):
    """
    Parse an AUTOSAR ARXML file and return
    structured information.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"ARXML file not found: {file_path}"
        )

    tree = ET.parse(file_path)
    root = tree.getroot()

    result = {
        "file_name": file_path.name,
        "root_element": get_local_name(root.tag),
        "named_elements": [],
    }

    for element in root.iter():

        tag = get_local_name(element.tag)

        if tag == "SHORT-NAME" and element.text:

            name = element.text.strip()

            if name:
                result["named_elements"].append(name)

    return result


if __name__ == "__main__":

    file_path = (
        "Input_Data/sample_hld/EcuExtract.arxml"
    )

    data = parse_arxml(file_path)

    print("ARXML parsing successful")
    print(f"File: {data['file_name']}")
    print(f"Root: {data['root_element']}")
    print(
        f"Named elements: "
        f"{len(data['named_elements'])}"
    )

    print("\nFirst 20 names:")

    for name in data["named_elements"][:20]:
        print(f"- {name}")