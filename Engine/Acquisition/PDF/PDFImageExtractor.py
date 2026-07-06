import fitz

from Engine.Documents.Image import Image
from Engine.Documents.Figure import Figure


class PDFImageExtractor:

    def extract(self, pdf, document):

        # Extract embedded images and best-effort bounding boxes.
        # PyMuPDF provides get_images(full=True) but bbox requires page-level text/search.
        # We use get_text("dict") to locate image placeholder rectangles in the block stream.
        for page_number in range(len(pdf)):
            pdf_page = pdf.load_page(page_number)

            text_dict = pdf_page.get_text("dict")

            # Attempt to locate image blocks
            for b in text_dict.get("blocks", []):
                if b.get("type") != 1:
                    # type=1 is typically image in PyMuPDF dict output
                    continue

                bbox = b.get("bbox")
                if not bbox or len(bbox) != 4:
                    continue

                img = Image()
                img.page = page_number + 1
                img.bbox = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))

                # dimensions
                img.width = float(bbox[2] - bbox[0])
                img.height = float(bbox[3] - bbox[1])

                img.type = "embedded"

                # pixels extraction: best-effort (extract the image by reference id when possible)
                # If xref not present in dict, keep pixels as None.
                xref = b.get("xref")
                if xref is not None:
                    try:
                        pix = fitz.Pixmap(pdf, xref)
                        img.pixels = pix.tobytes()
                        img.metadata["colorspace"] = getattr(pix, "colorspace", None)
                    except Exception:
                        img.pixels = None

                document.raw.images.append(img)

                # Also create Figure container for now; caption detection comes later in Sprint 3
                fig = Figure()
                fig.page = img.page
                fig.bbox = img.bbox
                fig.width = img.width
                fig.height = img.height
                fig.position = img.bbox
                fig.image = img
                document.raw.figures.append(fig)

        return document
