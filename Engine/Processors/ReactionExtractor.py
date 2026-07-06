from Engine.Interpretation.ReactionParser import ReactionParser
from Engine.Processors.Processor import Processor


class ReactionExtractor(Processor):

    def __init__(self, parser=None):

        super().__init__()

        self.parser = parser or ReactionParser()

    def process(self, document):

        schema = document.metadata.get("schema", {})

        if "Reaction" not in schema:

            document.reactions = []

            document.metadata["reaction_count"] = 0

            return document

        document.reactions = self.parser.parse(document, schema)

        document.metadata["reaction_count"] = len(document.reactions)

        return document
