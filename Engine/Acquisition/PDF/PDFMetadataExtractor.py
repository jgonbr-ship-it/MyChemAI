import fitz


class PDFMetadataExtractor:

    def extract(self, pdf, document):

        # Best-effort extraction using PyMuPDF metadata
        try:
            md = pdf.metadata or {}
        except Exception:
            md = {}

        document.metadata.setdefault("pdf", {})
        for k, v in md.items():
            if v is None:
                continue
            document.metadata["pdf"][str(k).lower()] = v

        # Also store per-file page count and default page size/orientation from first page
        try:
            page0 = pdf.load_page(0)
            rect = page0.rect
            document.metadata["pdf"].setdefault("page_width", float(rect.width))
            document.metadata["pdf"].setdefault("page_height", float(rect.height))
            try:
                document.metadata["pdf"].setdefault("rotation", int(page0.rotation))
            except Exception:
                pass
        except Exception:
            pass

        return document
