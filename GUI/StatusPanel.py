from PySide6.QtWidgets import QStatusBar


class StatusPanel(QStatusBar):

    def __init__(self):

        super().__init__()

        self.showMessage("MyChemAI iniciado correctamente.")