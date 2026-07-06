from Engine.Interpretation.ReactionParser import ReactionParser
from Engine.Processors.Processor import Processor


class ReactionExtractor(Processor):

    def __init__(self, parser=None):


        super().__init__()

        self.parser = parser or ReactionParser()

    def process(self, document):

        # Debug temporal profundo (solo logging)
        from Engine.Logger import Logger

        try:
            pages = getattr(document.raw, "pages", []) or []
            paragraphs = getattr(document.raw, "paragraphs", []) or []
            spans = getattr(document.raw, "spans", []) or []

            pages_count = len(pages)
            paragraphs_count = len(paragraphs)
            spans_count = len(spans)

            # Ejemplo de texto completo por página (primeros 300 chars)
            page_previews: list[str] = []
            for p in pages[:10]:
                page_text = getattr(p, "text", "") or ""
                page_previews.append(page_text[:300])

            # También preview del texto global si existe
            text_preview = getattr(document, "text", "") or ""
            if not text_preview:
                sentences = getattr(document.raw, "sentences", []) or []
                text_preview = " ".join([s.text for s in sentences[:1]]) if sentences else ""
            text_preview = str(text_preview)[:200]

            Logger.info(
                "[ReactionExtractor] pages=%s paragraphs=%s spans=%s total_preview='%s'",
                pages_count,
                paragraphs_count,
                spans_count,
                text_preview,
            )

            for i, prev in enumerate(page_previews, start=1):
                Logger.info("[ReactionExtractor] page_preview_%s='%s'", i, prev)

        except Exception:
            pass

        schema = document.metadata.get("schema", {})

        # Debug: schema detectado
        try:
            Logger.info(f"[ReactionExtractor] schema_detected_keys={list(schema.keys())}")
            if schema:
                for k, cols in schema.items():
                    Logger.info(f"[ReactionExtractor] schema[{k}] columns={cols}")
        except Exception:
            pass

        # Debug: evidencia de input químico que llega a ReactionParser
        try:
            if len(getattr(document, "tables", [])) == 0:
                Logger.info("[ReactionExtractor] document.tables=0")
            else:
                Logger.info(f"[ReactionExtractor] document.tables={len(document.tables)}")
                df = document.tables[0]
                Logger.info(f"[ReactionExtractor] table0 columns={list(getattr(df, 'columns', []))}")

                # Log de primeras filas (solo strings, limitadas)
                rxn_cols = schema.get("Reaction", [])
                for col in rxn_cols[:5]:
                    try:
                        Logger.info(f"[ReactionExtractor] evaluating_column='{col}'")
                        for i, v in enumerate(df[col].head(10)):
                            if i >= 10:
                                break
                            if isinstance(v, str):
                                s = v.strip()
                                Logger.info(f"  [input] row{i} len={len(s)} preview='{s[:120]}' contains='>>'={'>>' in s}")
                            else:
                                Logger.info(f"  [input] row{i} non-str type={type(v).__name__}")
                    except Exception:
                        pass
        except Exception:
            pass



        if "Reaction" not in schema:

            document.reactions = []

            document.metadata["reaction_count"] = 0

            return document

        document.reactions = self.parser.parse(document, schema)

        document.metadata["reaction_count"] = len(document.reactions)

        return document
