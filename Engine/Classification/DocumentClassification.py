from dataclasses import dataclass, field


@dataclass
class DocumentClassification:

    document_type: str = "UNKNOWN"
    contains_text: bool = False
    contains_tables: bool = False
    contains_images: bool = False
    contains_reactions: bool = False
    contains_molecules: bool = False
    contains_spectra: bool = False
    contains_references: bool = False
    contains_metadata: bool = False
    metadata: dict = field(default_factory=dict)

    def to_dict(self):

        return {

            "document_type": self.document_type,
            "contains_text": self.contains_text,
            "contains_tables": self.contains_tables,
            "contains_images": self.contains_images,
            "contains_reactions": self.contains_reactions,
            "contains_molecules": self.contains_molecules,
            "contains_spectra": self.contains_spectra,
            "contains_references": self.contains_references,
            "contains_metadata": self.contains_metadata,
            "metadata": self.metadata,

        }
