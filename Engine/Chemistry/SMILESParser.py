from rdkit import Chem
from rdkit.Chem import Descriptors


class SMILESParser:

    def parse(self, smiles):

        smiles = smiles.strip()

        molecule = Chem.MolFromSmiles(smiles)

        if molecule is None:

            return None

        info = {

            "smiles": smiles,

            "rdkit": molecule,

            "formula": Chem.rdMolDescriptors.CalcMolFormula(molecule),

            "molecular_weight": Descriptors.MolWt(molecule),

            "num_atoms": molecule.GetNumAtoms(),

            "num_bonds": molecule.GetNumBonds(),

            "num_rings": molecule.GetRingInfo().NumRings()

        }

        return info