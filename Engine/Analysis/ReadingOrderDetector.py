from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Any


@dataclass(frozen=True)
class ReadOrderItem:
    order: int
    page: int | None
    position: tuple[float, float, float, float] | None
    text: str
    block: Any


class ReadingOrderDetector:
    """Reconstructs reading order from blocks with coordinates.

    Assumes blocks have:
      - .page (int) OR can be None
      - .position = (x0, y0, x1, y1) as floats
      - .text

    Ordering heuristic:
      - sort by page
      - then by y0 (top-to-bottom)
      - then by x0 (left-to-right)
    """

    def order(self, blocks: Iterable[object]) -> list[ReadOrderItem]:
        items: list[ReadOrderItem] = []
        for i, b in enumerate(blocks):
            page = getattr(b, "page", None)
            pos = getattr(b, "position", None)
            text = getattr(b, "text", None) or ""
            if pos is not None and len(pos) == 4:
                try:
                    x0, y0, _, _ = pos
                    pos_t = (float(x0), float(y0), float(pos[2]), float(pos[3]))
                except Exception:
                    pos_t = None
            else:
                pos_t = None

            items.append(
                ReadOrderItem(
                    order=0,
                    page=page if isinstance(page, int) else None,
                    position=pos_t,
                    text=str(text),
                    block=b,
                )
            )

        def sort_key(it: ReadOrderItem):
            page = it.page if it.page is not None else 0
            if it.position is None:
                return (page, 0.0, 0.0)
            x0, y0, _, _ = it.position
            return (page, y0, x0)

        items_sorted = sorted(items, key=sort_key)
        for idx, it in enumerate(items_sorted):
            items_sorted[idx] = ReadOrderItem(
                order=idx,
                page=it.page,
                position=it.position,
                text=it.text,
                block=it.block,
            )
        return items_sorted

