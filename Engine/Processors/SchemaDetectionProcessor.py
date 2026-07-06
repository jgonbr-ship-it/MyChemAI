from Engine.Intelligence.SchemaDetector import SchemaDetector
from Engine.Processors.Processor import Processor


class SchemaDetectionProcessor(Processor):

    def __init__(self, detector=None):

        super().__init__()

        self.detector = detector or SchemaDetector()

    def process(self, document):

        # Debug temporal (solo logging)
        from Engine.Logger import Logger

        try:
            pages_count = len(getattr(document.raw, "pages", []))
            paragraphs_count = len(getattr(document.raw, "paragraphs", []))
            spans_count = len(getattr(document.raw, "spans", []))
            text_preview = getattr(document, "text", "") or ""
            if not text_preview:
                sentences = getattr(document.raw, "sentences", [])
                text_preview = " ".join([s.text for s in sentences[:1]]) if sentences else ""
            text_preview = str(text_preview)[:200]

            Logger.info(
                "[SchemaDetectionProcessor] pages=%s paragraphs=%s spans=%s preview='%s'",
                pages_count,
                paragraphs_count,
                spans_count,
                text_preview,
            )
        except Exception:
            pass

        if len(document.tables) == 0:


            document.metadata.setdefault("schema", {})

            return document

        schema = self.detector.detect(document.tables[0])

        document.metadata["schema"] = schema

        return document
