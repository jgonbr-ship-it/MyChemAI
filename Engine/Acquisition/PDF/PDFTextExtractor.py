from __future__ import annotations

import fitz

from Engine.Logger import Logger
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

        """Extrae texto de PDF manteniendo salida compatible (Page/Paragraph/Sentences).

        Optimizada para evitar O(n²) durante el mapeo de spans a párrafos.
        """

        def _safe_len(obj, attr: str):
            try:
                if obj is None:
                    return "N/A"
                if not hasattr(obj, attr):
                    return "N/A"
                value = getattr(obj, attr)
                return len(value)
            except Exception:
                return "N/A"

        def _safe_doc_attr(name: str):
            try:
                return _safe_len(document, name)
            except Exception:
                return "N/A"

        def _safe_raw_attr(attr: str):
            try:
                raw = getattr(document, "raw", None)
                return _safe_len(raw, attr)
            except Exception:
                return "N/A"

        Logger.info(
            "[AUDIT][PDFTextExtractor][START] path="
            f"{getattr(document, 'path', None)} "
            f"raw.pages={_safe_raw_attr('pages')} "
            f"raw.blocks={_safe_raw_attr('blocks')} "
            f"raw.lines={_safe_raw_attr('lines')} "
            f"raw.spans={_safe_raw_attr('spans')} "
            f"raw.paragraphs={_safe_raw_attr('paragraphs')} "
            f"tables={_safe_doc_attr('tables')} "
            f"images={_safe_doc_attr('images')} "
            f"reactions={_safe_doc_attr('reactions')} "
            f"molecules={_safe_doc_attr('molecules')}"
        )

        Logger.info("Inicio PDFTextExtractor")

        total_pages = len(pdf)

        for page_number in range(total_pages):

            Logger.info(f"Procesando página {page_number + 1}/{total_pages}")

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
            blocks_data = text_dict.get("blocks", [])

            blocks_out: list[PdfBlock] = []

            # Construcción de estructura por bloque.
            # Nota: Para mantener compatibilidad (Paragraph/Page), generamos Paragraphs
            # directamente cuando recorremos los bloques (sin O(n²) ni re-escaneo global).

            for b in blocks_data:

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

            # Construcción directa del modelo documental:
            # Page -> (Block -> Line -> Span) y Paragraph a partir del texto normalizado del bloque.
            # Para mantener compatibilidad, generamos un Paragraph por bloque.
            # Importante: eliminamos cualquier referencia a variables auxiliares externas.

            if blocks_out:
                # Usamos el mismo orden de blocks_data para aproximar lectura.
                for block in blocks_data:
                    block_type = block.get("type", 0)
                    if block_type not in (0, 1):
                        continue

                    bbox = block.get("bbox")
                    paragraph_bbox = tuple(bbox) if bbox and len(bbox) == 4 else None

                    spans_for_block: list[PdfSpan] = []
                    raw_parts: list[str] = []

                    for l in block.get("lines", []):
                        for s in l.get("spans", []):
                            t = s.get("text", "")
                            if not t:
                                continue
                            raw_parts.append(t)

                            # recuperar span desde document.raw.spans no es O(n²) aquí,
                            # porque no hacemos búsqueda; en su lugar creamos spans mínimos
                            # (mantenemos compatibilidad con Paragraph.spans consumido por GUI).
                            spans_for_block.append(
                                PdfSpan(
                                    text=t,
                                    font=s.get("font", None),
                                    size=float(s.get("size", 0)) if s.get("size", None) is not None else None,
                                    bold=self._detect_bold_italic(str(s.get("font", "")))[0],
                                    italic=self._detect_bold_italic(str(s.get("font", "")))[1],
                                    color=None,
                                    bbox=tuple(s.get("bbox", (0, 0, 0, 0))) if s.get("bbox") and len(s.get("bbox")) == 4 else None,
                                    page=page.number,
                                    order_index=len(document.raw.spans),
                                )
                            )

                    raw_text = self.normalizer.normalize("".join(raw_parts).strip())
                    if not raw_text:
                        continue

                    paragraph = Paragraph()
                    paragraph.text = raw_text
                    paragraph.page = page.number

                    if paragraph_bbox is not None:
                        paragraph.position = (
                            float(paragraph_bbox[0]),
                            float(paragraph_bbox[1]),
                            float(paragraph_bbox[2]),
                            float(paragraph_bbox[3]),
                        )

                    paragraph.spans = spans_for_block
                    paragraph.split_sentences()

                    page.paragraphs.append(paragraph)
                    document.raw.paragraphs.append(paragraph)
                    document.raw.sentences.extend(paragraph.sentences)



            page.blocks = blocks_out


            document.raw.pages.append(page)

            if (page_number + 1) % 50 == 0 or (page_number + 1) == total_pages:
                Logger.info(
                    "[AUDIT][PDFTextExtractor][PROGRESS] path="
                    f"{getattr(document, 'path', None)} page={page_number + 1}/{total_pages} "
                    f"raw.pages={_safe_raw_attr('pages')} "
                    f"raw.blocks={_safe_raw_attr('blocks')} "
                    f"raw.lines={_safe_raw_attr('lines')} "
                    f"raw.spans={_safe_raw_attr('spans')} "
                    f"raw.paragraphs={_safe_raw_attr('paragraphs')} "
                    f"tables={_safe_doc_attr('tables')} "
                    f"images={_safe_doc_attr('images')} "
                    f"reactions={_safe_doc_attr('reactions')} "
                    f"molecules={_safe_doc_attr('molecules')}"
                )

        Logger.info(
            "[AUDIT][PDFTextExtractor][END] path="
            f"{getattr(document, 'path', None)} "
            f"raw.pages={_safe_raw_attr('pages')} "
            f"raw.blocks={_safe_raw_attr('blocks')} "
            f"raw.lines={_safe_raw_attr('lines')} "
            f"raw.spans={_safe_raw_attr('spans')} "
            f"raw.paragraphs={_safe_raw_attr('paragraphs')} "
            f"tables={_safe_doc_attr('tables')} "
            f"images={_safe_doc_attr('images')} "
            f"reactions={_safe_doc_attr('reactions')} "
            f"molecules={_safe_doc_attr('molecules')}"
        )

        return document
