from rdkit import Chem


class ReactionAnalyzer:

    def analyze(self, reaction):

        analysis = {}

        analysis["num_reactants"] = len(reaction.reactants)
        analysis["num_products"] = len(reaction.products)

        analysis["contains_ring"] = False
        analysis["contains_aromatic"] = False
        analysis["contains_halogen"] = False
        analysis["contains_nitrogen"] = False
        analysis["contains_oxygen"] = False

        atoms = 0

        molecules = reaction.reactants + reaction.products

        for molecule in molecules:

            mol = molecule.rdkit

            atoms += mol.GetNumAtoms()

            if mol.GetRingInfo().NumRings() > 0:
                analysis["contains_ring"] = True

            for atom in mol.GetAtoms():

                symbol = atom.GetSymbol()

                if atom.GetIsAromatic():
                    analysis["contains_aromatic"] = True

                if symbol == "N":
                    analysis["contains_nitrogen"] = True

                if symbol == "O":
                    analysis["contains_oxygen"] = True

                if symbol in ["F", "Cl", "Br", "I"]:
                    analysis["contains_halogen"] = True

        analysis["total_atoms"] = atoms

        analysis["complexity_score"] = (
            atoms
            + analysis["num_reactants"] * 3
            + analysis["num_products"] * 3
        )

        return analysis