from Engine.Processors.Processor import Processor


class KnowledgeRegistrationProcessor(Processor):

    def __init__(self, knowledge_base):

        super().__init__()

        self.knowledge_base = knowledge_base

    def process(self, document):

        doc_id = self.knowledge_base.add_document(document)

        reaction_ids = []

        for reaction in document.reactions:

            reaction_id = self.knowledge_base.add_reaction(reaction)

            reaction_ids.append(reaction_id)

            for molecule in reaction.reactants + reaction.products:

                self.knowledge_base.add_molecule(molecule)

        for molecule in document.molecules:

            self.knowledge_base.add_molecule(molecule)

        for spectrum in document.spectra:

            self.knowledge_base.add_spectrum(spectrum)

        document.metadata["document_id"] = doc_id
        document.metadata["reaction_ids"] = reaction_ids

        return document
