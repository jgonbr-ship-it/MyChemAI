from Engine.Intelligence.SchemaDetector import SchemaDetector
from Engine.Processors.Processor import Processor


class SchemaDetectionProcessor(Processor):

    def __init__(self, detector=None):

        super().__init__()

        self.detector = detector or SchemaDetector()

    def process(self, document):

        if len(document.tables) == 0:

            document.metadata.setdefault("schema", {})

            return document

        schema = self.detector.detect(document.tables[0])

        document.metadata["schema"] = schema

        return document
