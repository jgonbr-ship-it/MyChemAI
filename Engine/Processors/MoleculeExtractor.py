from Engine.Processors.Processor import Processor


class MoleculeExtractor(Processor):

    def process(self, document):

        molecules = {}

        for reaction in document.reactions:

            for molecule in reaction.reactants + reaction.products:

                molecules[molecule.smiles] = molecule

        document.molecules = list(molecules.values())

        document.metadata["molecule_smiles"] = list(molecules.keys())

        return document
