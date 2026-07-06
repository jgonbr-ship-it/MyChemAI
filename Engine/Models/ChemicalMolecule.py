class ChemicalMolecule:

    def __init__(self, molecule_data):

        self.smiles = molecule_data["smiles"]

        self.formula = molecule_data["formula"]

        self.weight = molecule_data["molecular_weight"]

        self.num_atoms = molecule_data["num_atoms"]

        self.num_bonds = molecule_data["num_bonds"]

        self.num_rings = molecule_data["num_rings"]

        self.rdkit = molecule_data["rdkit"]

    def show(self):

        print("----------------------------")

        print("SMILES:", self.smiles)

        print("Formula:", self.formula)

        print("Peso molecular:", round(self.weight,3))

        print("Átomos:", self.num_atoms)

        print("Enlaces:", self.num_bonds)

        print("Anillos:", self.num_rings)