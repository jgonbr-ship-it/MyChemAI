from __future__ import annotations

from typing import List, Optional


from Engine.Documents.Page import Span


class Paragraph:


    def __init__(self):

        # Backward compatible fields
        self.text = ""

        self.page = 0

        self.position = None

        self.sentences = []

        self.entities = []

        # Advanced PDF paragraph model
        self.spans: List[Span] = []

        self.line_spacing: Optional[float] = None

        self.paragraph_spacing: Optional[float] = None

        self.heading_level: Optional[int] = None

        self.style_metadata: dict = {}

    def split_sentences(self):

        import re

        pieces = re.split(r'(?<=[.!?])\s+', self.text)

        from Engine.Documents.Structure.Sentece import Sentence


        self.sentences = []

        for piece in pieces:

            piece = piece.strip()

            if not piece:

                continue

            sentence = Sentence()

            sentence.text = piece

            sentence.page = self.page

            self.sentences.append(sentence)
