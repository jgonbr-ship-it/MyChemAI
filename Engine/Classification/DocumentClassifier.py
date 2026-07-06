from Engine.Classification.DocumentClassification import DocumentClassification


class DocumentClassifier:

    def classify(self, document):

        text = document.text or ""
        metadata = document.metadata or {}

        classification = DocumentClassification(
            document_type=document.type or "UNKNOWN",
            contains_text=len(text.strip()) > 0,
            contains_tables=len(document.tables) > 0,
            contains_images=len(document.images) > 0,
            contains_reactions=len(document.reactions) > 0,
            contains_molecules=len(document.molecules) > 0,
            contains_spectra=len(document.spectra) > 0,
            contains_references=self.detect_references(document),
            contains_metadata=len(metadata) > 0,
            metadata={
                "name": document.name,
                "source": document.source,
                "path": document.path,
                "table_count": len(document.tables),
                "image_count": len(document.images),
                "reaction_count": len(document.reactions),
                "molecule_count": len(document.molecules),
                "spectrum_count": len(document.spectra),
            },
        )

        return classification

    # ===================================

    def detect_references(self, document):

        if "references" in document.metadata:

            return bool(document.metadata["references"])

        text = (document.text or "").lower()

        return "references" in text or "bibliography" in text
