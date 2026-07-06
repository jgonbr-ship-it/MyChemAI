class Chapter:

    def __init__(self):

        self.number = None

        self.title = ""

        self.sections = []

        self.page_start = None

        self.page_end = None

    def add_section(self, section):

        self.sections.append(section)