from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Abbrev:
    abbreviation: str
    expanded: str


class AbbreviationResolver:
    """Learns abbreviation mappings and expands future occurrences.

    Supports patterns:
      - NMR (Nuclear Magnetic Resonance)
      - NMR: Nuclear Magnetic Resonance
    """

    _PAREN_RE = re.compile(
        r"\b(?P<abbr>[A-Z][A-Za-z0-9]{0,10})\b\s*\(\s*(?P<expanded>[^)]+?)\s*\)",
    )

    _COLON_RE = re.compile(
        r"\b(?P<abbr>[A-Z][A-Za-z0-9]{0,10})\b\s*[:\u2014\-–]\s*(?P<expanded>[^\n\.]{3,140})",
    )

    def __init__(self):
        self._map: dict[str, str] = {}

    def learn_from_text(self, text: str) -> list[Abbrev]:
        if not text:
            return []

        found: list[Abbrev] = []

        for m in self._PAREN_RE.finditer(text):
            abbr = m.group("abbr").strip()
            expanded = m.group("expanded").strip()
            if abbr and expanded:
                self._register(abbr, expanded)
                found.append(Abbrev(abbreviation=abbr, expanded=expanded))

        for m in self._COLON_RE.finditer(text):
            abbr = m.group("abbr").strip()
            expanded = m.group("expanded").strip()
            if abbr and expanded:
                self._register(abbr, expanded)
                found.append(Abbrev(abbreviation=abbr, expanded=expanded))

        return found

    def expand(self, text: str) -> str:
        if not text:
            return text

        out = text
        for abbr, expanded in self._map.items():
            # do not expand when it appears as part of the definition "ABBR (expanded)"
            out = re.sub(rf"\b{re.escape(abbr)}\b(?!\s*\()", expanded, out)
        return out

    def _register(self, abbr: str, expanded: str) -> None:
        if abbr not in self._map:
            self._map[abbr] = expanded

