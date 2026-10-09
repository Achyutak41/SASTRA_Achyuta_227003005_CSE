import json
import re
from pathlib import Path


class ArchitectureCleaningError(Exception):
    """Raised when architecture knowledge cannot be cleaned."""
    pass


class AUTOSARArchitectureCleaner:
    """
    Cleans deterministic AUTOSAR architecture extraction output.

    The original architecture JSON is never modified.
    A separate cleaned JSON is generated for downstream RAG/indexing.
    """

    STOPWORDS = {
        "a", "an", "and", "are", "as", "at", "be", "by",
        "for", "from", "has", "have", "in", "into", "is",
        "it", "its", "of", "on", "or", "that", "the",
        "their", "this", "to", "was", "were", "which",
        "with", "work", "only", "still", "also", "then",
        "than", "these", "those", "such", "can", "could",
        "should", "would", "will"
    }

    # Common AUTOSAR technical terms that are useful for
    # architecture knowledge extraction.
    TECHNICAL_TERMS = {
        "autosar",
        "sw-c",
        "software component",
        "rte",
        "bsw",
        "pdu",
        "pdu router",
        "com",
        "nvm",
        "dlt",
        "os",
        "api",
        "interface",
        "port",
        "signal",
        "runnable",
        "runnableentity",
        "scheduler",
        "driver",
        "microcontroller",
        "ecu",
        "service",
        "module",
        "communication",
        "serialization",
        "transformer",
        "mapping",
        "multiplexing",
        "synchronization",
        "stbm",
        "ethtsyn",
        "eth",
        "can",
        "lin",
        "flexray",
        "ethernet",
        "application",
        "memory",
        "diagnostic",
        "network",
        "event",
        "data",
        "client",
        "server",
        "provider",
        "required",
        "provided"
    }

    def __init__(self, processed_dir: str):
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def clean_architecture(self, document_id: str):
        """
        Load architecture extraction JSON, clean entities and
        relationships, and save a separate cleaned JSON.
        """

        input_path = (
            self.processed_dir /
            f"{document_id}_architecture.json"
        )

        if not input_path.exists():
            raise ArchitectureCleaningError(
                f"Architecture file not found: {input_path}"
            )

        try:
            with open(input_path, "r", encoding="utf-8") as file:
                architecture = json.load(file)
        except Exception as exc:
            raise ArchitectureCleaningError(
                f"Unable to read architecture JSON: {exc}"
            )

        cleaned_entities = self._clean_entities(
            architecture.get("entities", {})
        )

        cleaned_relationships = self._clean_relationships(
            architecture.get("relationships", []),
            cleaned_entities
        )

        knowledge_records = self._build_knowledge_records(
            cleaned_entities,
            cleaned_relationships
        )

        result = {
            "document_id": architecture.get("document_id"),
            "document_name": architecture.get("document_name"),
            "source_architecture_file": input_path.name,
            "cleaning_status": "success",

            "entities": cleaned_entities,

            "relationships": cleaned_relationships,

            "knowledge_records": knowledge_records,

            "statistics": {
                "raw_components": len(
                    architecture.get("entities", {}).get(
                        "components", []
                    )
                ),
                "raw_interfaces": len(
                    architecture.get("entities", {}).get(
                        "interfaces", []
                    )
                ),
                "raw_ports": len(
                    architecture.get("entities", {}).get(
                        "ports", []
                    )
                ),
                "raw_signals": len(
                    architecture.get("entities", {}).get(
                        "signals", []
                    )
                ),
                "raw_runnables": len(
                    architecture.get("entities", {}).get(
                        "runnables", []
                    )
                ),

                "clean_components": len(
                    cleaned_entities["components"]
                ),
                "clean_interfaces": len(
                    cleaned_entities["interfaces"]
                ),
                "clean_ports": len(
                    cleaned_entities["ports"]
                ),
                "clean_signals": len(
                    cleaned_entities["signals"]
                ),
                "clean_runnables": len(
                    cleaned_entities["runnables"]
                ),

                "raw_relationships": len(
                    architecture.get("relationships", [])
                ),
                "clean_relationships": len(
                    cleaned_relationships
                ),

                "knowledge_records": len(
                    knowledge_records
                )
            }
        }

        output_path = (
            self.processed_dir /
            f"{document_id}_architecture_clean.json"
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False
            )

        return result

    # ---------------------------------------------------------
    # Entity cleaning
    # ---------------------------------------------------------

    def _clean_entities(self, entities):
        cleaned = {
            "components": [],
            "interfaces": [],
            "ports": [],
            "signals": [],
            "runnables": []
        }

        for entity_type in cleaned.keys():

            raw_items = entities.get(entity_type, [])

            seen = set()

            for item in raw_items:

                name = str(item.get("name", "")).strip()

                if not self._valid_entity_name(name):
                    continue

                key = (
                    entity_type,
                    name.lower(),
                    item.get("page")
                )

                if key in seen:
                    continue

                seen.add(key)

                cleaned[entity_type].append({
                    "name": name,
                    "page": item.get("page"),
                    "section": item.get("section")
                })

        return cleaned

    # ---------------------------------------------------------
    # Entity validation
    # ---------------------------------------------------------

    def _valid_entity_name(self, name: str) -> bool:

        if not name:
            return False

        if len(name) > 100:
            return False

        normalized = name.lower().strip()

        # Reject ordinary stopwords.
        if normalized in self.STOPWORDS:
            return False

        # Reject very short ordinary words.
        if len(normalized) <= 2:
            return False

        # Reject names consisting only of punctuation.
        if not re.search(r"[A-Za-z0-9]", name):
            return False

        # Strong technical indicators.
        if self._contains_technical_term(normalized):
            return True

        # AUTOSAR-style naming:
        # SW-C, Rte_xxx, CanIf, PduR, NvM, etc.
        if "-" in name:
            return True

        # Acronyms / mixed-case technical identifiers.
        if re.search(r"[A-Z]{2,}", name):
            return True

        if re.search(r"[a-z]+[A-Z][A-Za-z0-9]*", name):
            return True

        # Generic lowercase English words should not become
        # architecture entities.
        return False

    def _contains_technical_term(self, normalized: str) -> bool:

        for term in self.TECHNICAL_TERMS:

            if normalized == term:
                return True

            if term in normalized:
                return True

        return False

    # ---------------------------------------------------------
    # Relationship cleaning
    # ---------------------------------------------------------

    def _clean_relationships(
        self,
        relationships,
        cleaned_entities
    ):

        cleaned = []

        # Build names that survived entity validation.
        valid_entity_names = set()

        for entity_type, items in cleaned_entities.items():
            for item in items:
                valid_entity_names.add(
                    item["name"].lower()
                )

        seen = set()

        for relation in relationships:

            source = str(
                relation.get("source", "")
            ).strip()

            target = str(
                relation.get("target", "")
            ).strip()

            relationship_type = str(
                relation.get("relationship", "")
            ).strip()

            if not source or not target:
                continue

            if relationship_type not in {
                "requires",
                "provides",
                "uses",
                "communicates with"
            }:
                continue

            if not self._valid_relation_term(source):
                continue

            if not self._valid_relation_term(target):
                continue

            # At least one side should correspond to an
            # extracted technical entity.
            if (
                source.lower() not in valid_entity_names
                and target.lower() not in valid_entity_names
                and not self._contains_technical_term(
                    source.lower()
                )
                and not self._contains_technical_term(
                    target.lower()
                )
            ):
                continue

            key = (
                source.lower(),
                relationship_type,
                target.lower(),
                relation.get("page")
            )

            if key in seen:
                continue

            seen.add(key)

            cleaned.append({
                "source": source,
                "relationship": relationship_type,
                "target": target,
                "page": relation.get("page"),
                "section": relation.get("section")
            })

        return cleaned

    def _valid_relation_term(self, value: str) -> bool:

        normalized = value.lower().strip()

        if not normalized:
            return False

        if normalized in self.STOPWORDS:
            return False

        # Reject phrases beginning or ending with
        # obvious grammatical words.
        tokens = normalized.split()

        if tokens[0] in self.STOPWORDS:
            return False

        if tokens[-1] in self.STOPWORDS:
            return False

        if len(tokens) > 6:
            return False

        if not re.search(r"[A-Za-z0-9]", value):
            return False

        return True

    # ---------------------------------------------------------
    # RAG knowledge records
    # ---------------------------------------------------------

    def _build_knowledge_records(
        self,
        entities,
        relationships
    ):

        records = []

        # Entity records
        for entity_type, items in entities.items():

            for item in items:

                text = (
                    f"AUTOSAR {entity_type[:-1] if entity_type.endswith('s') else entity_type}: "
                    f"{item['name']}."
                )

                records.append({
                    "type": "architecture_entity",
                    "entity_type": entity_type,
                    "name": item["name"],
                    "text": text,
                    "page": item.get("page"),
                    "section": item.get("section")
                })

        # Relationship records
        for relation in relationships:

            text = (
                f"AUTOSAR architecture relationship: "
                f"{relation['source']} "
                f"{relation['relationship']} "
                f"{relation['target']}."
            )

            records.append({
                "type": "architecture_relationship",
                "source": relation["source"],
                "relationship": relation["relationship"],
                "target": relation["target"],
                "text": text,
                "page": relation.get("page"),
                "section": relation.get("section")
            })

        return records