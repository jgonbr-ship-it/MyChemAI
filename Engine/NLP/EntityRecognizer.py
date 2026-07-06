from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Entity:
    type: str
    text: str
    start: int | None = None
    end: int | None = None
    meta: dict[str, str] | None = None


class EntityRecognizer:
    """Recognizes molecules, reactions, formulas, CAS numbers, and units."""

    _CAS_RE = re.compile(r"\b\d{2,7}-\d{2}-\d{1,2}\b")

    _FORMULA_RE = re.compile(r"\b(?:[A-Z][a-z]?\d*){1,6}(?:\^?[-+]?\d+)?\b")

    _UNIT_RE = re.compile(
        r"\b(?:mM|\u00b5M|uM|nM|g|mg|kg|mol|mmol|\u00b0C|K|Pa|kPa|MPa|cm\u22121|cm\-1|s|sec|min|h|hr|L|mL|\%|%|J|kJ|eV)\b",
        flags=re.IGNORECASE,
    )

    _REACTION_RE = re.compile(r"(>>|->|→|⇌|<->|⇄)")

    # Very rough SMILES-ish heuristic: letters plus typical SMILES punctuation.
    _SMILES_RE = re.compile(r"\b[BCDFHIKLMNOPRSTVWYbcdfhiklmnostvwxyz0-9@+\-\\/\[\](){}=#$:.]+\b")

    _CHEM_NAME_RE = re.compile(r"\b(?:[A-Z][a-z]+)(?:\s+[A-Z][a-z0-9]+){0,5}\b")

    def recognize(self, text: str) -> list[Entity]:
        if not text:
            return []

        entities: list[Entity] = []

        # Reactions
        if self._REACTION_RE.search(text):
            entities.append(
                Entity(type="reaction", text=self._reaction_snippet(text))
            )

        # CAS
        for m in self._CAS_RE.finditer(text):
            entities.append(
                Entity(type="cas", text=m.group(0), start=m.start(), end=m.end())
            )

        # Units
        for m in self._UNIT_RE.finditer(text):
            entities.append(
                Entity(type="unit", text=m.group(0), start=m.start(), end=m.end())
            )

        # Formulas
        for m in self._FORMULA_RE.finditer(text):
            tok = m.group(0)
            if re.fullmatch(r"[A-Za-z]+", tok):
                continue
            entities.append(
                Entity(type="formula", text=tok, start=m.start(), end=m.end())
            )

        # Molecules: SMILES-ish OR chemical names heuristic
        for m in self._SMILES_RE.finditer(text):
            tok = m.group(0)
            if len(tok) < 6:
                continue
            entities.append(
                Entity(type="molecule", text=tok, start=m.start(), end=m.end())
            )

        for m in self._CHEM_NAME_RE.finditer(text):
            tok = m.group(0)
            if len(tok) < 3:
                continue
            lowered = tok.lower()
            if lowered in {
                "abstract",
                "introduction",
                "methods",
                "results",
                "discussion",
                "conclusion",
                "keywords",
            }:
                continue
            entities.append(
                Entity(type="molecule", text=tok, start=m.start(), end=m.end())
            )

        # de-duplicate
        seen: set[tuple[str, str]] = set()
        out: list[Entity] = []
        for e in entities:
            key = (e.type, e.text)
            if key in seen:
                continue
            seen.add(key)
            out.append(e)

        return out

    def _reaction_snippet(self, text: str) -> str:
        m = self._REACTION_RE.search(text)
        if not m:
            return text[:120]
        start = max(0, m.start() - 80)
        end = min(len(text), m.end() + 140)
        return text[start:end].strip()

