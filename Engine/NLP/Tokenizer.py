from __future__ import annotations

import re


class Tokenizer:
    """Tokenizer for scientific/chemical text.

    Preserves:
      - chemical formulas (e.g., C6H6, SO4^2-, NH4+)
      - reaction arrows (->, →, ⇌, <->)
      - CAS numbers
      - units

    Output is a list of tokens.
    """

    _REACTION_ARROW_RE = re.compile(r"(->|→|⇌|<->|⇄)")

    _CAS_RE = re.compile(r"\b\d{2,7}-\d{2}-\d{1,2}\b")

    _UNIT_RE = re.compile(
        r"\b(?:mM|\u00b5M|uM|nM|g|mg|kg|mol|mmol|\u00b0C|K|Pa|kPa|MPa|cm\u22121|cm\-1|s|sec|min|h|hr|L|mL|\%|%|J|kJ|eV)\b",
        flags=re.IGNORECASE,
    )

    _FORMULA_STRICT_RE = re.compile(
        r"\b(?:[A-Z][a-z]?\d*){1,6}(?:\^?[-+]?\d+)?\b"
    )

    _TOKEN_RE = re.compile(r"\s*(\d+(?:\.\d+)?)|\s*([A-Za-z_\u00b5][A-Za-z0-9_\u00b5\-]*)|\s*(->|→|⇌|<->|⇄)|\s*(\d{2,7}-\d{2}-\d{1,2})|\s*(\S)")

    def tokenize(self, text: str) -> list[str]:
        if not text:
            return []

        t = text.replace("\r", "\n")
        t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)
        t = self._REACTION_ARROW_RE.sub(r" \1 ", t)

        tokens: list[str] = []
        i = 0
        while i < len(t):
            if t[i].isspace():
                i += 1
                continue

            m = self._CAS_RE.match(t, i)
            if m:
                tokens.append(m.group(0))
                i = m.end(0)
                continue

            m = self._UNIT_RE.match(t, i)
            if m:
                tokens.append(m.group(0))
                i = m.end(0)
                continue

            m = self._FORMULA_STRICT_RE.match(t, i)
            if m:
                tok = m.group(0)
                # Avoid plain words matched as formulas
                if not re.fullmatch(r"[A-Za-z]+", tok):
                    tokens.append(tok)
                    i = m.end(0)
                    continue

            # default token: consume non-space chunk
            j = i
            while j < len(t) and not t[j].isspace():
                j += 1
            tokens.append(t[i:j])
            i = j

        return [tok for tok in (tok.strip() for tok in tokens) if tok]

