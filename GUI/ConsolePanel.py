from PySide6.QtWidgets import QTextEdit


class ConsolePanel(QTextEdit):

    def __init__(self):

        super().__init__()

        self.setReadOnly(True)

        self.setMaximumHeight(180)

        self.append("========== MyChemAI Console ==========\n")

    def log(self, text):

        self.append(text)