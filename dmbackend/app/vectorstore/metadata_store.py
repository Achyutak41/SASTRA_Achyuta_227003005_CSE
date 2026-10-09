import json
import os


class MetadataStore:

    def __init__(self):
        self.items = []

    def add(self, metadata):
        self.items.append(metadata)

    def add_many(self, metadata_items):
        self.items.extend(metadata_items)

    def get(self, index):
        if index < 0 or index >= len(self.items):
            return None

        return self.items[index]

    def all(self):
        return self.items

    def save(self, path):
        directory = os.path.dirname(path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                self.items,
                file,
                indent=2,
                ensure_ascii=False
            )

    @classmethod
    def load(cls, path):
        store = cls()

        with open(path, "r", encoding="utf-8") as file:
            store.items = json.load(file)

        return store