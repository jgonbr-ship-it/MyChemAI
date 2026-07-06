from __future__ import annotations

from typing import Iterable, Any

from Engine.Analysis.HeadingDetector import HeadingDetector


class SectionDetector:
    """Organizes reading-order paragraphs into sections.

    Input: iterable of paragraph-like objects exposing:
      - .text
      - .page

    Output: list of Section-like objects with:
      - .title
      - .page
      - .add_paragraph(paragraph)

    Uses the existing Engine.Layout.Section model when available.
    """

    def __init__(self, heading_detector: HeadingDetector | None = None):
        self.heading_detector = heading_detector or HeadingDetector()

        # Lazy import to avoid circular issues
        from Engine.Layout.Section import Section as LayoutSection

        self._section_cls = LayoutSection

    def detect(self, paragraphs: Iterable[object]) -> list[object]:
        sections: list[object] = []
        current_section: object | None = None

        for p in paragraphs:
            block_like = p
            if self.heading_detector.is_heading(block_like):
                current_section = self._section_cls()
                current_section.title = getattr(p, "text", "")
                current_section.page = getattr(p, "page", None)
                sections.append(current_section)
                continue

            if current_section is None:
                # If no heading seen yet, create a default "Document" section.
                current_section = self._section_cls()
                current_section.title = "Document"
                current_section.page = getattr(p, "page", None)
                sections.append(current_section)

            current_section.add_paragraph(p)

        return sections

