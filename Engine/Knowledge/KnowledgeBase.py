class KnowledgeBase:

    def __init__(self):

        self.documents = {}
        self.reactions = {}
        self.molecules = {}
        self.spectra = {}

        self.document_counter = 0
        self.reaction_counter = 0
        self.molecule_counter = 0
        self.spectrum_counter = 0

    # ===========================
    # DOCUMENTOS
    # ===========================

    def add_document(self, document):

        self.document_counter += 1

        doc_id = f"DOC{self.document_counter:06d}"

        self.documents[doc_id] = document

        return doc_id

    # ===========================
    # REACCIONES
    # ===========================

    def add_reaction(self, reaction):

        self.reaction_counter += 1

        reaction_id = f"RXN{self.reaction_counter:06d}"

        self.reactions[reaction_id] = reaction

        return reaction_id

    # ===========================
    # MOLECULAS
    # ===========================

    def add_molecule(self, molecule):

        key = molecule.smiles

        if key in self.molecules:

            return key

        self.molecule_counter += 1

        self.molecules[key] = molecule

        return key

    # ===========================
    # ESPECTROS
    # ===========================

    def add_spectrum(self, spectrum):

        self.spectrum_counter += 1

        spectrum_id = f"SPC{self.spectrum_counter:06d}"

        self.spectra[spectrum_id] = spectrum

        return spectrum_id

    # ===========================
    # ESTADISTICAS
    # ===========================

    def statistics(self):

        return {

            "documents": len(self.documents),

            "reactions": len(self.reactions),

            "molecules": len(self.molecules),

            "spectra": len(self.spectra),

        }
