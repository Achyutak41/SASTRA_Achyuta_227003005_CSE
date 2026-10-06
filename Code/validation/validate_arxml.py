import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


ARXML_FILE = Path(
    "Input_Data/sample_hld/EcuExtract.arxml"
)


def get_local_name(tag):
    """
    Removes XML namespace from a tag.

    Example:
    {http://autosar.org/schema/r4.0}AR-PACKAGES
    becomes:
    AR-PACKAGES
    """
    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag


def main():

    if not ARXML_FILE.exists():
        print(f"ERROR: File not found: {ARXML_FILE}")
        return

    print("=" * 60)
    print("AUTOSAR ARXML DATASET VALIDATION")
    print("=" * 60)

    print(f"\nInput file:")
    print(ARXML_FILE)

    # Parse XML
    try:
        tree = ET.parse(ARXML_FILE)
        root = tree.getroot()
    except ET.ParseError as error:
        print("\nERROR: Invalid XML file")
        print(error)
        return

    print("\nXML validation: SUCCESS")
    print(f"Root element: {get_local_name(root.tag)}")

    # Count all XML elements
    tag_counter = Counter()

    for element in root.iter():
        tag_counter[get_local_name(element.tag)] += 1

    print("\n" + "-" * 60)
    print("MOST COMMON AUTOSAR ELEMENTS")
    print("-" * 60)

    for tag, count in tag_counter.most_common(30):
        print(f"{tag:55} {count}")

    # Important AUTOSAR architecture elements
    important_elements = {
        "Software Components": [
            "APPLICATION-SW-COMPONENT-TYPE",
            "SERVICE-SW-COMPONENT-TYPE",
            "COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE",
        ],
        "Ports": [
            "P-PORT-PROTOTYPE",
            "R-PORT-PROTOTYPE",
        ],
        "Interfaces": [
            "SENDER-RECEIVER-INTERFACE",
            "CLIENT-SERVER-INTERFACE",
        ],
        "Data Elements": [
            "VARIABLE-DATA-PROTOTYPE",
            "DATA-ELEMENT",
        ],
        "Runnables": [
            "SWC-BSW-MAPPING",
            "RUNNABLE-ENTITY",
        ],
        "Connectors": [
            "ASSEMBLY-SW-CONNECTOR",
            "DELEGATION-SW-CONNECTOR",
        ],
        "Compositions": [
            "COMPOSITION-SW-COMPONENT-TYPE",
        ],
        "System Information": [
            "SYSTEM",
            "SYSTEM-SIGNAL",
            "ECUC-MODULE-CONFIGURATION-VALUES",
        ],
    }

    print("\n" + "-" * 60)
    print("IMPORTANT AUTOSAR ELEMENTS")
    print("-" * 60)

    for category, tags in important_elements.items():

        print(f"\n{category}:")

        found = False

        for tag in tags:
            count = tag_counter.get(tag, 0)

            if count > 0:
                print(f"  {tag}: {count}")
                found = True

        if not found:
            print("  None found")

    # Extract names
    print("\n" + "-" * 60)
    print("NAMED AUTOSAR ELEMENTS")
    print("-" * 60)

    names = []

    for element in root.iter():

        tag = get_local_name(element.tag)

        if tag == "SHORT-NAME" and element.text:
            name = element.text.strip()

            if name:
                names.append(name)

    print(f"\nTotal named elements found: {len(names)}")

    print("\nFirst 30 names:")

    for name in names[:30]:
        print(f"  - {name}")

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()