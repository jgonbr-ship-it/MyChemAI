class Section:

    def __init__(self):

        self.type = None

        self.title = ""

        self.page = 0

        self.blocks = []

    def add_block(self, block):

        self.blocks.append(block)