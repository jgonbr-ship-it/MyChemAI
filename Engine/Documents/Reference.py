from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


BBox = Tuple[float, float, float, float]


class Reference:

    def __init__(self):

        # Backward compatible fields
        self.authors = None

        self.title = None

        self.journal = None

        self.doi = None

        self.year = None

        # Advanced
        self.raw_text: str = ""

        self.page: int = 0

        self.bbox: Optional[BBox] = None

        self.parsed_fields: Dict[str, Any] = {}

