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

        """Detecta columnas de un esquema usando señales del contenido real.

        Mantiene la API actual: recibe un "dataframe" con atributo "columns" y retorna
        un dict {Field: [column_names]}.

        Soporta además un fallback cuando el "dataframe" no sea usable:
        - Si el documento no aporta tablas, se puede llamar a este método con una
          estructura equivalente (p. ej. un objeto con atributo columns=None/ausente).
        """

        schema: dict[str, list[str]] = {}

        Logger.info("")
        Logger.info("========== SCHEMA DETECTOR ==========")

        if len(self.knowledge) == 0:
            Logger.info("No existe conocimiento para detectar columnas.")
            return schema

        # Patrones/tokens químicos/palabras clave
        reaction_patterns = [">>", "->", "=", "+", "rxn", "smiles"]
        yield_keywords = ["yield", "rendimiento", "conversion", "percent", "%"]
        temp_keywords = [
            "temperature",
            "temp",
            "celsius",
            "c",
            "°c",
            "kelvin",
            "k",
        ]


        def _iter_values(df, col_name, limit_rows=50):

            # Log del tipo de contenedor (DataFrame vs Table del modelo documental)
            try:
                from Engine.Documents.Table import Table as DocumentTable  # local import to avoid cycles
            except Exception:
                DocumentTable = None  # type: ignore[assignment]

            is_table = DocumentTable is not None and isinstance(df, DocumentTable)

            if is_table:
                try:
                    Logger.info(f"[SchemaDetector] _iter_values source=Table col='{col_name}'")

                    # col_name puede no ser un índice numérico (p. ej. 'col_0')
                    if not hasattr(df, "columns") or not df.columns:
                        return []

                    # localizar índice de columna
                    try:
                        col_idx = df.columns.index(col_name)
                    except ValueError:
                        # si col_name no existe exactamente, intentar parsear 'col_{i}'
                        try:
                            if isinstance(col_name, str) and col_name.startswith("col_"):
                                col_idx = int(col_name.split("_", 1)[1])
                            else:
                                return []
                        except Exception:
                            return []

                    out: list[str] = []
                    for row in getattr(df, "rows", [])[:limit_rows]:
                        cells = getattr(row, "cells", []) or []
                        if col_idx < 0 or col_idx >= len(cells):
                            continue
                        cell_text = getattr(cells[col_idx], "text", None)
                        if cell_text is None:
                            continue
                        s = str(cell_text).strip()
                        if not s:
                            continue
                        s_low = s.lower()
                        if s_low in {"nan", "none", "null"}:
                            continue
                        out.append(s)

                    return out[:limit_rows]
                except Exception:
                    return []

            # Comportamiento original: pandas.DataFrame u objeto tipo DataFrame
            try:
                Logger.info(f"[SchemaDetector] _iter_values source=DataFrame-like col='{col_name}'")
            except Exception:
                pass

            try:
                series = df[col_name]
            except Exception:
                return []

            out = []
            try:
                for i, v in enumerate(series):
                    if i >= limit_rows:
                        break
                    if v is None:
                        continue
                    s = str(v).strip()
                    if not s:
                        continue
                    s_low = s.lower()
                    if s_low in {"nan", "none", "null"}:
                        continue
                    out.append(s)
            except Exception:
                return []

            return out

        def _score_field(field, values):

            joined = " ".join(values).lower()

            score = 0

            for alias in self.knowledge.get(field, []):

                alias_l = str(alias).lower()

                if alias_l and alias_l in joined:

                    score += 20

            if field == "Reaction":

                for p in reaction_patterns:

                    if p in joined:

                        score += 25

            elif field == "Yield":

                if any(k in joined for k in yield_keywords):

                    score += 35

            elif field == "Temperature":

                if any(k in joined for k in temp_keywords):

                    score += 35

            return min(score, 100)

        # Si no hay tablas, fallback sobre el texto (párrafos) para detectar schema global.
        # Nota: mantenemos la API de retorno ({Field: [column_names]}), así que en fallback
        # devolvemos nombres sintéticos por consistencia.
        if not hasattr(dataframe, "columns") or dataframe is None or dataframe.columns is None:

            try:
                paragraphs = getattr(dataframe, "paragraphs", None)
            except Exception:
                paragraphs = None

            if not paragraphs:
                Logger.info("[SchemaDetector] Sin columnas ni párrafos compatibles para fallback.")
                return schema

            text_values: list[str] = []
            for p in paragraphs[:2000]:
                try:
                    t = getattr(p, "text", None)
                except Exception:
                    t = None
                if not t:
                    continue
                t = str(t).strip()
                if t:
                    text_values.append(t)

            joined = " ".join(text_values).lower()

            # Puntuar por field usando el mismo algoritmo de scoring existente (score_field)
            # construyendo un conjunto de valores.
            def _score_global(field: str) -> int:
                values = [joined]
                joined_local = " ".join(values).lower()
                score = 0

                for alias in self.knowledge.get(field, []):
                    alias_l = str(alias).lower()
                    if alias_l and alias_l in joined_local:
                        score += 20

                if field == "Reaction":
                    for p in reaction_patterns:
                        if p in joined_local:
                            score += 25
                elif field == "Yield":
                    if any(k in joined_local for k in yield_keywords):
                        score += 35
                elif field == "Temperature":
                    if any(k in joined_local for k in temp_keywords):
                        score += 35

                return min(score, 100)

            Logger.info("[SchemaDetector] Fallback sobre párrafos (tabla ausente).")
            for field in self.knowledge.keys():
                best_score = _score_global(field)
                if best_score >= self.threshold:
                    # nombre sintético: se mantiene contrato de [column_names]
                    schema.setdefault(field, []).append("__paragraph_text__")

            return schema

        for column in dataframe.columns:



            scores_name = self.score_column(column)

            values = _iter_values(dataframe, column)

            # Debug input real que usa SchemaDetector (solo logs, sin cambiar lógica)
            try:
                joined_preview = " ".join(values).replace("\n", " ")[:500]
                Logger.info(f"\n[SchemaDetector] Columna='{column}'")
                Logger.info(f"[SchemaDetector] values_preview='{joined_preview}'")

                t = " ".join(values).lower()
                features: set[str] = set()

                for p in [">>", "->", "=", "+", "rxn", "smiles"]:
                    if p in t:
                        features.add(p)

                for kw in ["yield", "rendimiento", "conversion", "percent", "%"]:
                    if kw in t:
                        features.add(kw)

                for kw in [
                    "temperature",
                    "temp",
                    "celsius",
                    "c",
                    "°c",
                    "kelvin",
                    "k",
                ]:
                    if kw in t:
                        features.add(kw)

                Logger.info(f"[SchemaDetector] features_detectadas={sorted(features)}")
            except Exception:
                pass

            scores_content = {
                field: _score_field(field, values)
                for field in scores_name.keys()
            }


            scores = {
                field: 0.45 * scores_name[field] + 0.55 * scores_content[field]
                for field in scores_name.keys()
            }

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

