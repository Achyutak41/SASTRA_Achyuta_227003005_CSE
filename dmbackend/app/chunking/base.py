from dataclasses import dataclass
from typing import Optional


@dataclass
class Chunk:
    text: str

    page_number: Optional[int] = None

    section_title: Optional[str] = None

    chunk_index: int = 0

    chunking_strategy: str = ""

    chunk_size: Optional[int] = None

    chunk_overlap: Optional[int] = None

    character_count: int = 0

    token_count: Optional[int] = None

    def __post_init__(self):
        self.text = self.text.strip()

        self.character_count = len(
            self.text
        )

        if self.token_count is None:
            self.token_count = (
                len(
                    self.text.split()
                )
            )