from pathlib import Path

from Engine.Documents.Document import Document


class Reader:

    def __init__(self):

        self.file = None

    def create_document(self, filepath, document_type):

        filepath = Path(filepath)

        document = Document()

        document.name = filepath.name
        document.path = str(filepath)
        document.type = document_type
        document.source = "Local File"

        return document

    def load(self, filepath):

        raise NotImplementedError(
            "Cada Reader debe implementar load()."
        )