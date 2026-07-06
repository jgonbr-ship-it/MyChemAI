from Engine.Layout.Section import Section
from Engine.Layout.SectionType import SectionType


class SectionDetector:

    def __init__(self):

        self.section_titles = {

            "abstract": SectionType.ABSTRACT,

            "keywords": SectionType.KEYWORDS,

            "introduction": SectionType.INTRODUCTION,

            "background": SectionType.BACKGROUND,

            "experimental": SectionType.EXPERIMENTAL,

            "materials": SectionType.MATERIALS,

            "methods": SectionType.METHODS,

            "results": SectionType.RESULTS,

            "discussion": SectionType.DISCUSSION,

            "conclusion": SectionType.CONCLUSION,

            "acknowledgements": SectionType.ACKNOWLEDGEMENTS,

            "references": SectionType.REFERENCES,

            "supporting information": SectionType.SUPPORTING_INFORMATION
        }

    def detect(self, layout_pages):

        sections = []

        current = None

        for page in layout_pages:

            for block in page.blocks:

                text = block.text.strip().lower()

                if text in self.section_titles:

                    current = Section()

                    current.type = self.section_titles[text]

                    current.title = block.text

                    current.page = page.number

                    sections.append(current)

                    continue

                if current is not None:

                    current.add_block(block)

        return sections