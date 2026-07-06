import json
import math
from datetime import datetime, timezone
from pathlib import Path

from Engine.Chemistry.SMILESParser import SMILESParser
from Engine.Documents.Document import Document
from Engine.Knowledge.KnowledgeBase import KnowledgeBase
from Engine.Models.ChemicalMolecule import ChemicalMolecule
from Engine.Models.ChemicalReaction import ChemicalReaction


class KnowledgeStorage:

    VERSION = 1

    def __init__(self, default_path=None):

        self.project_root = Path(__file__).resolve().parents[2]
        self.default_path = self.resolve_path(default_path or "Database/knowledge_base.json")
        self.smiles_parser = SMILESParser()

    # ===================================

    def resolve_path(self, filepath=None):

        if filepath is None:

            return self.default_path

        path = Path(filepath)

        if path.is_absolute():

            return path

        return self.project_root / path

    # ===================================

    def exists(self, filepath=None):

        return self.resolve_path(filepath).exists()

    # ===================================

    def save(self, knowledge_base, filepath=None):

        path = self.resolve_path(filepath)

        path.parent.mkdir(parents=True, exist_ok=True)

        payload = self.to_dict(knowledge_base)

        with open(path, "w", encoding="utf-8") as file:

            json.dump(payload, file, ensure_ascii=False, indent=2)

        return path

    # ===================================

    def load(self, filepath=None):

        path = self.resolve_path(filepath)

        with open(path, "r", encoding="utf-8") as file:

            payload = json.load(file)

        return self.from_dict(payload)

    # ===================================

    def to_dict(self, knowledge_base):

        return {

            "version": self.VERSION,

            "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),

            "statistics": knowledge_base.statistics(),

            "counters": {

                "document_counter": knowledge_base.document_counter,

                "reaction_counter": knowledge_base.reaction_counter,

                "molecule_counter": knowledge_base.molecule_counter,

                "spectrum_counter": knowledge_base.spectrum_counter,

            },

            "documents": {

                document_id: self._document_to_dict(document)
                for document_id, document in knowledge_base.documents.items()

            },

            "molecules": {

                smiles: self._molecule_to_dict(molecule)
                for smiles, molecule in knowledge_base.molecules.items()

            },

            "reactions": {

                reaction_id: self._reaction_to_dict(reaction)
                for reaction_id, reaction in knowledge_base.reactions.items()

            },

            "spectra": {

                spectrum_id: self._object_to_dict(spectrum)
                for spectrum_id, spectrum in knowledge_base.spectra.items()

            },

        }

    # ===================================

    def from_dict(self, payload):

        knowledge_base = KnowledgeBase()

        for document_id, document_data in payload.get("documents", {}).items():

            knowledge_base.documents[document_id] = self._document_from_dict(document_data)

        for smiles, molecule_data in payload.get("molecules", {}).items():

            molecule = self._molecule_from_dict(molecule_data)

            if molecule is not None:

                knowledge_base.molecules[smiles] = molecule

        for reaction_id, reaction_data in payload.get("reactions", {}).items():

            reaction = self._reaction_from_dict(reaction_data)

            knowledge_base.reactions[reaction_id] = reaction

            for molecule in reaction.reactants + reaction.products:

                if molecule.smiles not in knowledge_base.molecules:

                    knowledge_base.molecules[molecule.smiles] = molecule

        knowledge_base.spectra = payload.get("spectra", {})

        counters = payload.get("counters", {})

        knowledge_base.document_counter = counters.get(
            "document_counter",
            self._max_numeric_id(knowledge_base.documents, "DOC"),
        )

        knowledge_base.reaction_counter = counters.get(
            "reaction_counter",
            self._max_numeric_id(knowledge_base.reactions, "RXN"),
        )

        knowledge_base.molecule_counter = counters.get(
            "molecule_counter",
            len(knowledge_base.molecules),
        )

        knowledge_base.spectrum_counter = counters.get(
            "spectrum_counter",
            self._max_numeric_id(knowledge_base.spectra, "SPC"),
        )

        return knowledge_base

    # ===================================

    def _document_to_dict(self, document):

        loaded_at = document.loaded_at

        if isinstance(loaded_at, datetime):

            loaded_at = loaded_at.isoformat(timespec="seconds")

        table_summaries = [

            self._table_summary(table)
            for table in document.tables

        ]

        return {

            "name": document.name,

            "source": document.source,

            "type": document.type,

            "path": document.path,

            "loaded_at": loaded_at,

            "text": document.text,

            "metadata": self._json_safe(document.metadata),

            "table_summaries": table_summaries,

            "counts": {

                "tables": len(document.tables),

                "images": len(document.images),

                "reactions": len(document.reactions),

                "molecules": len(document.molecules),

                "spectra": len(document.spectra),

                "conditions": len(document.conditions),

            },

        }

    # ===================================

    def _document_from_dict(self, data):

        document = Document()

        document.name = data.get("name")
        document.source = data.get("source")
        document.type = data.get("type")
        document.path = data.get("path")
        document.text = data.get("text", "")
        document.metadata = data.get("metadata", {})

        loaded_at = data.get("loaded_at")

        if loaded_at:

            document.loaded_at = self._parse_datetime(loaded_at)

        if data.get("table_summaries"):

            document.metadata.setdefault("table_summaries", data["table_summaries"])

        return document

    # ===================================

    def _reaction_to_dict(self, reaction):

        reactants = [molecule.smiles for molecule in reaction.reactants]
        products = [molecule.smiles for molecule in reaction.products]

        return {

            "reaction_smiles": f"{'.'.join(reactants)}>>{'.'.join(products)}",

            "reactants": reactants,

            "products": products,

            "reactant_details": [

                self._molecule_to_dict(molecule)
                for molecule in reaction.reactants

            ],

            "product_details": [

                self._molecule_to_dict(molecule)
                for molecule in reaction.products

            ],

        }

    # ===================================

    def _reaction_from_dict(self, data):

        reaction = ChemicalReaction()

        for smiles in data.get("reactants", []):

            reaction.add_reactant(smiles)

        for smiles in data.get("products", []):

            reaction.add_product(smiles)

        return reaction

    # ===================================

    def _molecule_to_dict(self, molecule):

        return {

            "smiles": molecule.smiles,

            "formula": molecule.formula,

            "molecular_weight": molecule.weight,

            "num_atoms": molecule.num_atoms,

            "num_bonds": molecule.num_bonds,

            "num_rings": molecule.num_rings,

        }

    # ===================================

    def _molecule_from_dict(self, data):

        smiles = data.get("smiles")

        if not smiles:

            return None

        molecule_data = self.smiles_parser.parse(smiles)

        if molecule_data is None:

            molecule_data = {

                "smiles": smiles,

                "rdkit": None,

                "formula": data.get("formula"),

                "molecular_weight": data.get("molecular_weight", 0.0),

                "num_atoms": data.get("num_atoms", 0),

                "num_bonds": data.get("num_bonds", 0),

                "num_rings": data.get("num_rings", 0),

            }

        return ChemicalMolecule(molecule_data)

    # ===================================

    def _table_summary(self, table):

        shape = getattr(table, "shape", None)
        columns = getattr(table, "columns", [])

        rows = None

        if shape is not None and len(shape) > 0:

            rows = int(shape[0])

        return {

            "rows": rows,

            "columns": [str(column) for column in columns],

        }

    # ===================================

    def _object_to_dict(self, item):

        if hasattr(item, "__dict__"):

            return self._json_safe(item.__dict__)

        return self._json_safe(item)

    # ===================================

    def _json_safe(self, value):

        if value is None or isinstance(value, (str, int, bool)):

            return value

        if isinstance(value, float):

            if math.isfinite(value):

                return value

            return None

        if isinstance(value, datetime):

            return value.isoformat(timespec="seconds")

        if isinstance(value, Path):

            return str(value)

        if isinstance(value, dict):

            return {

                str(key): self._json_safe(item)
                for key, item in value.items()

            }

        if isinstance(value, (list, tuple, set)):

            return [

                self._json_safe(item)
                for item in value

            ]

        return str(value)

    # ===================================

    def _parse_datetime(self, value):

        try:

            return datetime.fromisoformat(value)

        except ValueError:

            return datetime.now()

    # ===================================

    def _max_numeric_id(self, values, prefix):

        maximum = 0

        for identifier in values:

            if not identifier.startswith(prefix):

                continue

            try:

                maximum = max(maximum, int(identifier.replace(prefix, "", 1)))

            except ValueError:

                continue

        return maximum
