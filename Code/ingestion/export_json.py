import json
from pathlib import Path

from arxml_parser import parse_arxml


INPUT_FILE = (
    "Input_Data/sample_hld/EcuExtract.arxml"
)

OUTPUT_DIR = Path("Input_Data/processed")

OUTPUT_FILE = OUTPUT_DIR / "EcuExtract.json"


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    data = parse_arxml(INPUT_FILE)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("JSON export successful")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()