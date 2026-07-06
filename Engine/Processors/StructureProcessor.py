from Engine.Analysis.DocumentStructureBuilder import DocumentStructureBuilder


class StructureProcessor:

    def __init__(self):

        self.builder = DocumentStructureBuilder()

    def process(self, document):

        print("Pipeline: StructureProcessor")

        return self.builder.build(document)