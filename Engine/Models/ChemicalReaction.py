from Engine.Chemistry.SMILESParser import SMILESParser
from Engine.Models.ChemicalMolecule import ChemicalMolecule


class ChemicalReaction:

    def __init__(self):

        self.reactants = []
        self.products = []

        self.parser = SMILESParser()

    def add_reactant(self, smiles):

        molecule_data = self.parser.parse(smiles)

        if molecule_data is not None:

            molecule = ChemicalMolecule(molecule_data)

            self.reactants.append(molecule)

    def add_product(self, smiles):

        molecule_data = self.parser.parse(smiles)

        if molecule_data is not None:

            molecule = ChemicalMolecule(molecule_data)

            self.products.append(molecule)

    def show(self):

        print("\n========== CHEMICAL REACTION ==========\n")

        print("Reactivos\n")

        for molecule in self.reactants:

            molecule.show()

        print("\nProductos\n")

        for molecule in self.products:

            molecule.show()