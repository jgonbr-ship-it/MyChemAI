from __future__ import annotations

import re


class SentenceSplitter:
    """High quality sentence splitter for scientific text.

    Improves over naive regex by protecting common abbreviations,
    protecting chemical formulas, and handling line breaks.
    """

    _ABBREV = {
        "e.g.",
        "i.e.",
        "et al.",
        "Fig.",
        "al.",
        "Dr.",
        "Prof.",
        "Sr.",
        "Jr.",
        "vs.",
        "No.",
        "Eq.",
        "Refs.",
    }

    _BOUNDARY_RE = re.compile(r"([.!?]+)(\s+)")

    def __init__(self):
        pass

    def split(self, text: str) -> list[str]:
        if not text:
            return []

        t = text.replace("\r", "\n")
        t = re.sub(r"[\t]+", " ", t)
        t = re.sub(r"\n{3,}", "\n\n", t)

        placeholders: list[str] = []

        def _protect(match: re.Match[str]) -> str:
            s = match.group(0)
            token = f"__ABBR_{len(placeholders)}__"
            placeholders.append(s)
            return token

        if self._ABBREV:
            abbrev_pattern = "|".join(
                re.escape(a) for a in sorted(self._ABBREV, key=len, reverse=True)
            )
            t = re.sub(abbrev_pattern, _protect, t, flags=re.IGNORECASE)

        # Avoid splitting inside chemical formulas like H2O, CO2, NH3
        t = re.sub(r"\b([A-Z][a-z]?)(\d+)(\b)", r"\1\2\3", t)

        # Convert internal line breaks to spaces
        t = re.sub(r"(?<!\n)\n(?!\n)", " ", t)

        parts: list[str] = []
        start = 0
        for m in self._BOUNDARY_RE.finditer(t):
            punct = m.group(1)
            end_ws = m.group(2)

            candidate = t[start : m.end(1)].strip()
            if not candidate:
                start = m.end(0)
                continue

            # Heuristic: if it ends with a single letter abbreviation, skip.
            if punct == "." and re.search(r"\b[A-Za-z]$", candidate):
                continue

            parts.append(candidate)
            start = m.end(0)

        tail = t[start:].strip()
        if tail:
            parts.append(tail)

        # Restore placeholders
        restored: list[str] = []
        for p in parts:
            for i, ab in enumerate(placeholders):
                p = p.replace(f"__ABBR_{i}__", ab)
            p = p.strip()
            if p:
                restored.append(p)

        # Merge tiny trailing fragments that are likely continuations
        merged: list[str] = []
        for s in restored:
            if merged and len(s) < 10 and not re.search(r"[.!?]\s*$", merged[-1]):
                merged[-1] = merged[-1] + " " + s
            else:
                merged.append(s)

        return merged

