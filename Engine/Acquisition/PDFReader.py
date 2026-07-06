import fitz

from Engine.Acquisition.Reader import Reader
from Engine.Logger import Logger

from Engine.Acquisition.PDF.PDFMetadataExtractor import PDFMetadataExtractor
from Engine.Acquisition.PDF.PDFTextExtractor import PDFTextExtractor
from Engine.Acquisition.PDF.PDFTableExtractor import PDFTableExtractor
from Engine.Acquisition.PDF.PDFImageExtractor import PDFImageExtractor


class PDFReader(Reader):

    def __init__(self):

        super().__init__()

        self.metadata = PDFMetadataExtractor()
        self.text = PDFTextExtractor()
        self.tables = PDFTableExtractor()
        self.images = PDFImageExtractor()

    def load(self, filepath):

        document = self.create_document(filepath, "PDF")

        pdf = None
        try:
            pdf = fitz.open(document.path)

            # Isolate extractors: if one fails (common with some PDFs),
            # the whole application must not crash.
            try:
                self.metadata.extract(pdf, document)
            except Exception as e:
                Logger.info(f"PDFMetadataExtractor fallo: {e}")

            try:
                self.text.extract(pdf, document)
            except Exception as e:
                Logger.info(f"PDFTextExtractor fallo: {e}")

            try:
                self.tables.extract(pdf, document)
            except Exception as e:
                Logger.info(f"PDFTableExtractor fallo: {e}")

            try:
                self.images.extract(pdf, document)
            except Exception as e:
                Logger.info(f"PDFImageExtractor fallo: {e}")

        finally:
            if pdf is not None:
                try:
                    pdf.close()
                except Exception:
                    pass

        Logger.info("PDF cargado correctamente.")
        return document

