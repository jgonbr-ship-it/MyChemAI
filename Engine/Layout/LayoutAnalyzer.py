from Engine.Layout.LayoutPage import LayoutPage
from Engine.Layout.LayoutBlock import LayoutBlock
from Engine.Layout.LayoutTypes import LayoutType


class LayoutAnalyzer:

    def analyze(self, pdf):

        layout_pages = []

        for page_number in range(len(pdf)):

            pdf_page = pdf.load_page(page_number)

            page = LayoutPage()

            page.number = page_number + 1

            blocks = pdf_page.get_text("blocks")

            for block in blocks:

                text = block[4].strip()

                if not text:

                    continue

                layout = LayoutBlock()

                layout.text = text

                layout.page = page.number

                layout.position = (

                    block[0],

                    block[1],

                    block[2],

                    block[3]

                )

                layout.type = LayoutType.PARAGRAPH

                page.blocks.append(layout)

            layout_pages.append(page)

        return layout_pages