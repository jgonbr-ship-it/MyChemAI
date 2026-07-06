from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


BBox = Tuple[float, float, float, float]


class Figure:

    def __init__(self):

        # Backward compatible
        self.image = None

        self.caption = None

        self.page = 0

        self.position = None

        # Advanced
        self.bbox: Optional[BBox] = None

        self.width: Optional[float] = None

        self.height: Optional[float] = None

        self.metadata: Dict[str, Any] = {}

