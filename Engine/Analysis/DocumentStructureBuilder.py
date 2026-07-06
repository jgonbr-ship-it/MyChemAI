from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from Engine.Analysis.ReadingOrderDetector import ReadingOrderDetector
from Engine.Analysis.SectionDetector import SectionDetector
from Engine.NLP.AbbreviationResolver import AbbreviationResolver
from Engine.NLP.SentenceSplitter import SentenceSplitter


class DocumentStructureBuilder:
    """Creates a hierarchical document tree on top of document.raw.

    Backward compatible:
      - it does not remove existing document.raw.sections.
      - it sets document.raw.sections based on paragraph reading order.
      - it also fills sentence splitting for paragraphs.

    It operates using existing paragraph/sentence objects:
      - paragraphs: Engine.Documents.Paragraph.Paragraph
      - sentences: Engine.Documents.Structure.Sentence
    """

    def __init__(
        self,
        *,
        reading_order_detector: ReadingOrderDetector | None = None,
        section_detector: SectionDetector | None = None,
    ):
        self.reading_order_detector = reading_order_detector or ReadingOrderDetector()
        self.section_detector = section_detector or SectionDetector()
        self.sentence_splitter = SentenceSplitter()
        self.abbrev_resolver = AbbreviationResolver()

    def build(self, document: Any) -> Any:
        # Ensure raw exists
        if not hasattr(document, "raw") or document.raw is None:
            return document

        # 1) Build reading order from existing raw.paragraphs
        paragraphs = list(getattr(document.raw, "paragraphs", []) or [])
        if not paragraphs:
            return document

        ordered_items = self.reading_order_detector.order(paragraphs)
        ordered_paragraphs = [it.block for it in ordered_items]

        # 2) Abbreviation learning + expansion across text stream
        #    This is light-weight and improves downstream entity recognition.
        running_text = "\n".join(getattr(p, "text", "") or "" for p in ordered_paragraphs[:200])
        self.abbrev_resolver.learn_from_text(running_text)

        for p in ordered_paragraphs:
            text = getattr(p, "text", "") or ""
            try:
                p.text = self.abbrev_resolver.expand(text)
            except Exception:
                pass

        # 3) Re-split sentences (higher quality splitter)
        for p in ordered_paragraphs:
            text = getattr(p, "text", "") or ""
            if not text:
                continue
            sentences = self.sentence_splitter.split(text)
            p.sentences = []

            from Engine.Documents.Structure.Sentece import Sentence

            page = getattr(p, "page", None)


            for s in sentences:
                sent = Sentence()
                sent.text = s
                sent.page = page
                p.sentences.append(sent)

        # 4) Section detection
        sections = self.section_detector.detect(ordered_paragraphs)

        # Keep backward compatibility: use document.raw.sections
        document.raw.sections = sections

        # Also rebuild flat sentences list for compatibility with existing GUI/logic
        document.raw.sentences = []
        for p in ordered_paragraphs:
            for s in getattr(p, "sentences", []) or []:
                document.raw.sentences.append(s)

        return document

