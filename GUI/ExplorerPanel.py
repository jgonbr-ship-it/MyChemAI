from PySide6.QtWidgets import QListWidget


class ExplorerPanel(QListWidget):

    def __init__(self):

        super().__init__()

        self.setMaximumWidth(250)

        self.show_empty()

    def show_empty(self):

        self.clear()

        self.addItem("Documentos")

        self.addItem("Moleculas")

        self.addItem("Reacciones")

        self.addItem("Espectros")

        self.addItem("IA")

    def show_database_summary(self, stats):

        self.clear()

        self.addItem(f"Documentos ({stats['documents']})")

        self.addItem(f"Reacciones ({stats['reactions']})")

        self.addItem(f"Moleculas ({stats['molecules']})")

        self.addItem(f"Espectros ({stats['spectra']})")

        self.addItem("IA")
