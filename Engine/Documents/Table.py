from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


BBox = Tuple[float, float, float, float]


@dataclass
class TableCell:

    text: str = ""

    bbox: Optional[BBox] = None

    row: int = 0

    col: int = 0


@dataclass
class TableRow:

    cells: List[TableCell]

    bbox: Optional[BBox] = None


@dataclass
class TableCellGrid:

    rows: List[TableRow]

    bbox: Optional[BBox] = None


class Table:

    def __init__(self):

        # Backward compatible attributes (existing code may attach)
        self.dataframe = None

        self.title = None

        self.caption = None

        self.page = 0

        self.position = None

        # Advanced PDF table model
        self.rows: List[TableRow] = []

        self.columns: List[str] = []

        self.cells: List[TableCell] = []

        self.bbox: Optional[BBox] = None
