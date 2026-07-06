import json
from pathlib import Path

from rapidfuzz import fuzz

from Engine.Logger import Logger


class SchemaDetector:

    def __init__(self, knowledge_path=None):

        self.threshold = 75

        self.knowledge = {}

        self.knowledge_path = (
            Path(knowledge_path)
            if knowledge_path is not None
            else Path(__file__).resolve().parents[1] / "Knowledge" / "Schemas"
        )

        self.load_knowledge()

        self.load_default_knowledge()

    # =====================================

    def load_knowledge(self):

        if not self.knowledge_path.exists():

            Logger.info(f"{self.knowledge_path} no existe. Usando conocimiento interno.")

            return

        for file in self.knowledge_path.glob("*.json"):

            try:

                with open(file, "r", encoding="utf-8") as schema_file:

                    data = json.load(schema_file)

                field = self.normalize_field_name(file.stem)

                self.merge_aliases(field, data.get("aliases", []))

            except Exception as error:

                Logger.info(f"Error cargando {file.name}: {error}")

    # =====================================

    def load_default_knowledge(self):

        defaults = {

            "Reaction": [
                "reaction",
                "reactions",
                "original_reaction",
                "updated_reaction",
                "rxn",
                "smiles",
                "reaction_smiles",
                "reaction smiles",
            ],

            "Yield": [
                "yield",
                "conversion",
                "percent",
                "yield_percent",
                "yield (%)",
            ],

            "Temperature": [
                "temperature",
                "temp",
                "celsius",
                "temperature_c",
            ],

            "Solvent": [
                "solvent",
                "solvents",
            ],

            "Catalyst": [
                "catalyst",
                "catalysts",
            ],

            "Time": [
                "time",
                "reaction_time",
                "hours",
                "minutes",
            ],

        }

        for field, aliases in defaults.items():

            self.merge_aliases(field, aliases)

    # =====================================

    def merge_aliases(self, field, aliases):

        known_aliases = self.knowledge.setdefault(field, [])

        for alias in aliases:

            if alias not in known_aliases:

                known_aliases.append(alias)

    # =====================================

    def normalize_field_name(self, name):

        if not name:

            return name

        return name[:1].upper() + name[1:]

    # =====================================

    def score_column(self, column_name):

        scores = {}

        column = str(column_name).lower()

        for field, aliases in self.knowledge.items():

            best = 0

            for alias in aliases:

                score = fuzz.ratio(column, str(alias).lower())

                if score > best:

                    best = score

            scores[field] = best

        return scores

    # =====================================

    def detect(self, dataframe):

        schema = {}

        Logger.info("")

        Logger.info("========== SCHEMA DETECTOR ==========")

        if len(self.knowledge) == 0:

            Logger.info("No existe conocimiento para detectar columnas.")

            return schema

        for column in dataframe.columns:

            scores = self.score_column(column)

            best_field = max(scores, key=scores.get)

            best_score = scores[best_field]

            Logger.info(f"\nColumna: {column}")

            for field, score in scores.items():

                Logger.info(f"{field:15} {score:.1f}%")

            if best_score >= self.threshold:

                schema.setdefault(best_field, []).append(column)

                Logger.info(f"--> Detectada como {best_field}")

            else:

                Logger.info("--> Sin clasificar")

        return schema
