from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class HeadingCandidate:
    text: str
    score: float
    level: int


class HeadingDetector:
    """Detects likely headings in extracted text blocks.

    Works with any object exposing at least:
      - .text (str)
      - optional .font_size (float/int)

    If font size is missing, relies on heuristics:
      - full capitalization / title case density
      - short length
      - numbering patterns like "1.", "2.3", "3)".
      - presence of common heading keywords.
    """

    _NUMBERING_RE = re.compile(
        r"^\s*(?:chapter|section)?\s*(\d+(?:[\.-]\d+){0,5})\s*(?:[\.|\)|:|-])\s+.+$",
        re.IGNORECASE,
    )
    _LEADING_NUMBER_RE = re.compile(r"^\s*(\d+(?:[\.-]\d+)*)\s*(?:[\.|\)|:|-])\s*\S.*$")

    _KEYWORD_HEADINGS = {
        "abstract",
        "keywords",
        "introduction",
        "background",
        "experimental",
        "materials",
        "methods",
        "results",
        "discussion",
        "conclusion",
        "conclusions",
        "acknowledgements",
        "acknowledgments",
        "references",
        "supporting information",
        "appendix",
    }

    def __init__(self, *, min_text_len: int = 3, max_text_len: int = 120):
        self.min_text_len = min_text_len
        self.max_text_len = max_text_len

    def detect(self, blocks: Iterable[object]) -> list[HeadingCandidate]:
        candidates: list[HeadingCandidate] = []
        for block in blocks:
            text = getattr(block, "text", None) or ""
            text = str(text).strip()
            if not text:
                continue
            cand = self._score(text, getattr(block, "font_size", None))
            if cand is None:
                continue
            candidates.append(cand)
        return sorted(candidates, key=lambda c: (-c.score, c.level))

    def is_heading(self, block: object) -> bool:
        text = str(getattr(block, "text", "") or "").strip()
        if not text:
            return False
        font_size = getattr(block, "font_size", None)
        cand = self._score(text, font_size)
        if cand is None:
            return False
        return cand.score >= 0.6

    def _score(self, text: str, font_size: Optional[float]) -> Optional[HeadingCandidate]:
        # Length constraint
        if not (self.min_text_len <= len(text) <= self.max_text_len):
            return None

        # Reject sentences (end punctuation often indicates paragraph text)
        if re.search(r"[.!?]\s*$", text) and len(text.split()) > 8:
            return None

        lowered = text.lower()

        # Common keyword headings
        if lowered in self._KEYWORD_HEADINGS:
            return HeadingCandidate(text=text, score=0.95, level=1)

        # Numbering headings
        level = 1
        m = self._LEADING_NUMBER_RE.match(text)
        if m:
            numbering = m.group(1)
            parts = re.split(r"[\.-]", numbering)
            level = min(6, len(parts))
            # Slightly boost numbered headings
            base = 0.75
        else:
            base = 0.45

        # Capitalization heuristic
        words = [w for w in re.split(r"\s+", text) if w]
        if not words:
            return None

        upper_ratio = sum(1 for w in words if w.isupper() and len(w) > 1) / len(words)
        title_ratio = sum(1 for w in words if w[:1].isupper() and w[1:].islower()) / len(words)

        # If font size is available, it often correlates with heading-ness.
        font_boost = 0.0
        if font_size is not None:
            try:
                fs = float(font_size)
                # Heuristic: bigger font => higher score.
                # Typical body sizes are ~9-12; headings often >= 13.
                if fs >= 16:
                    font_boost = 0.3
                elif fs >= 13:
                    font_boost = 0.18
                elif fs >= 12:
                    font_boost = 0.08
                else:
                    font_boost = -0.05
            except Exception:
                font_boost = 0.0

        # Reject if it looks like a long sentence
        if len(words) > 18 and not m:
            return None

        # Keyword density inside heading line
        kw_hits = sum(1 for kw in self._KEYWORD_HEADINGS if kw in lowered)
        kw_boost = 0.15 if kw_hits else 0.0

        score = base + font_boost + kw_boost + 0.2 * min(1.0, upper_ratio) + 0.1 * min(1.0, title_ratio)

        # Must contain at least one alphabetic character
        if not re.search(r"[A-Za-z]", text):
            return None

        if score < 0.55:
            return None

        return HeadingCandidate(text=text, score=float(score), level=level)

