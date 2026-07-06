import fitz

from Engine.Documents.Page import Block as PdfBlock
from Engine.Documents.Page import Line as PdfLine
from Engine.Documents.Page import Page, Span as PdfSpan
from Engine.Documents.Paragraph import Paragraph
from Engine.Text.TextNormalizer import TextNormalizer



class PDFTextExtractor:

    def __init__(self):

        self.normalizer = TextNormalizer()

    def _detect_bold_italic(self, font_name: str) -> tuple[bool, bool]:

        if not font_name:
            return False, False

        name = str(font_name).lower()

        bold = "bold" in name or name.endswith("-b")

        italic = "italic" in name or "oblique" in name

        return bold, italic

    def extract(self, pdf, document):

        # Keep backward compatible output (paragraphs/sentences/pages)
        for page_number in range(len(pdf)):

            pdf_page = pdf.load_page(page_number)

            page = Page()

            page.number = page_number + 1

            # Page geometry
            rect = pdf_page.rect

            page.width = float(rect.width)

            page.height = float(rect.height)

            # PyMuPDF does not expose rotation consistently across versions; attempt best-effort
            try:
                page.rotation = int(pdf_page.rotation)
            except Exception:
                page.rotation = None

            # Full page text (normalized)
            page.text = self.normalizer.normalize(pdf_page.get_text("text"))

            # Extract spans with formatting via get_text("dict")
            text_dict = pdf_page.get_text("dict")

            blocks_out: list[PdfBlock] = []

            # Also attach paragraphs with bbox from block-level aggregation
            for b in text_dict.get("blocks", []):

                block_type = b.get("type", 0)
                if block_type not in (0, 1):
                    continue

                bbox = tuple(b.get("bbox", (None, None, None, None)))
                if bbox[0] is None:
                    bbox = None

                block_out = PdfBlock(bbox=bbox)

                # lines
                for l in b.get("lines", []):

                    line_out = PdfLine(spans=[])

                    line_bbox = l.get("bbox")
                    if line_bbox:
                        line_out.bbox = tuple(line_bbox)

                    for s in l.get("spans", []):

                        span_text = s.get("text", "")
                        if not span_text:
                            continue

                        font = s.get("font", None)
                        size = s.get("size", None)

                        bold, italic = self._detect_bold_italic(str(font))

                        color = s.get("color", None)
                        # PyMuPDF color is usually int packed; keep raw float tuple if possible
                        color_rgb = None
                        if color is not None:
                            try:
                                # best-effort unpack
                                c = int(color)
                                r = (c >> 16) & 0xFF
                                g = (c >> 8) & 0xFF
                                b_ = c & 0xFF
                                color_rgb = (r / 255.0, g / 255.0, b_ / 255.0)
                            except Exception:
                                color_rgb = None

                        span_bbox = s.get("bbox", None)
                        span_bbox_t = tuple(span_bbox) if span_bbox else None

                        order_index = len(document.raw.spans)

                        pdf_span = PdfSpan(
                            text=span_text,
                            font=font,
                            size=float(size) if size is not None else None,
                            bold=bold,
                            italic=italic,
                            color=color_rgb,
                            bbox=span_bbox_t,
                            page=page.number,
                            order_index=order_index,
                        )

                        line_out.spans.append(pdf_span)
                        document.raw.spans.append(pdf_span)

                    if line_out.spans:
                        blocks_out.append(block_out)
                        block_out.lines.append(line_out)

            # If dict blocks did not populate paragraphs, create paragraphs from blocks using span text
            # This preserves current behavior with enriched spans.
            # We create one Paragraph per (block bbox) by concatenating span texts in reading order.
            # NOTE: document.raw.paragraphs historically expects Paragraph instances.
            for b in text_dict.get("blocks", []):

                bbox = b.get("bbox", None)
                if not bbox or len(bbox) != 4:
                    continue

                lines = b.get("lines", [])
                parts = []
                for l in lines:
                    for s in l.get("spans", []):
                        t = s.get("text", "")
                        if t:
                            parts.append(t)

                raw_text = "".join(parts).strip()
                raw_text = self.normalizer.normalize(raw_text)
                if not raw_text:
                    continue

                paragraph = Paragraph()
                paragraph.text = raw_text
                paragraph.page = page.number
                paragraph.position = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))

                # Attach spans that fall inside bbox (best-effort: just add spans from dict order)
                # We do not compute geometric inclusion per span for performance; keep paragraph model consistent.
                # spans list will contain at least the spans extracted during dict traversal order.
                paragraph.spans = [sp for sp in document.raw.spans if sp.page == page.number]

                paragraph.split_sentences()
                page.paragraphs.append(paragraph)
                document.raw.paragraphs.append(paragraph)
                document.raw.sentences.extend(paragraph.sentences)

            page.blocks = blocks_out

            document.raw.pages.append(page)

        return document
