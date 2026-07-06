from Engine.Processors.Processor import Processor


class MoleculeExtractor(Processor):

    def process(self, document):

        # Debug temporal (solo logging)
        from Engine.Logger import Logger

        try:
            pages_count = len(getattr(document.raw, "pages", []))
            paragraphs_count = len(getattr(document.raw, "paragraphs", []))
            spans_count = len(getattr(document.raw, "spans", []))
            text_preview = getattr(document, "text", "") or ""
            if not text_preview:
                sentences = getattr(document.raw, "sentences", [])
                text_preview = " ".join([s.text for s in sentences[:1]]) if sentences else ""
            text_preview = str(text_preview)[:200]

            Logger.info(
                "[MoleculeExtractor] pages=%s paragraphs=%s spans=%s preview='%s'",
                pages_count,
                paragraphs_count,
                spans_count,
                text_preview,
            )
        except Exception:
            pass

        molecules = {}


        for reaction in document.reactions:

            for molecule in reaction.reactants + reaction.products:

                molecules[molecule.smiles] = molecule

        document.molecules = list(molecules.values())

        document.metadata["molecule_smiles"] = list(molecules.keys())

        return document
