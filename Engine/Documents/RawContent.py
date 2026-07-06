class RawContent:

    def __init__(self):

        # Backward compatible containers
        self.pages = []

        self.paragraphs = []

        self.sentences = []

        self.tables = []

        self.figures = []

        self.images = []

        self.references = []

        self.sections = []

        self.chapters = []

        # Advanced containers (kept separate to avoid breaking existing code)
        self.blocks = []

        self.lines = []

        self.spans = []
