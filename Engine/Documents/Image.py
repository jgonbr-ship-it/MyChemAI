from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


BBox = Tuple[float, float, float, float]


class Image:

    def __init__(self):

        # Backward compatible
        self.pixels = None

        self.page = 0

        self.type = None

        self.metadata: Dict[str, Any] = {}

        # Advanced
        self.bbox: Optional[BBox] = None

        self.width: Optional[float] = None

        self.height: Optional[float] = None
