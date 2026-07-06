from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


BBox = Tuple[float, float, float, float]


@dataclass
class Span:

    text: str = ""

    font: Optional[str] = None

    size: Optional[float] = None

    bold: bool = False

    italic: bool = False

    color: Optional[Tuple[float, float, float]] = None

    bbox: Optional[BBox] = None

    page: int = 0

    order_index: int = 0


@dataclass
class Line:

    spans: List[Span] = field(default_factory=list)

    bbox: Optional[BBox] = None


@dataclass
class Block:

    lines: List[Line] = field(default_factory=list)

    bbox: Optional[BBox] = None


class Page:

    def __init__(self):

        self.number = 0

        # Backward compatible fields
        self.text = ""

        self.paragraphs = []

        self.tables = []

        self.figures = []

        self.images = []

        # Advanced PDF model
        self.width: Optional[float] = None

        self.height: Optional[float] = None

        self.rotation: Optional[int] = None

        self.blocks: List[Block] = []

        # Optional: allow external ordering to attach an index
        self.order_index: int = 0

