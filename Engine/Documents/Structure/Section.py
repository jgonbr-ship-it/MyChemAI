class Section:

    def __init__(self):

        self.number = None

        self.title = ""

        self.paragraphs = []

        self.tables = []

        self.figures = []

        self.images = []

        self.reactions = []

        self.molecules = []

        self.page = None

    def add_paragraph(self, paragraph):

        self.paragraphs.append(paragraph)