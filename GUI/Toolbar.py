from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar


class Toolbar(QMenuBar):

    def __init__(self):

        super().__init__()

        self.create_menus()

    def create_menus(self):

        archivo = self.addMenu("Archivo")

        self.open_csv = QAction("Abrir documento", self)

        archivo.addAction(self.open_csv)

        self.addMenu("Editar")

        self.addMenu("Ver")

        self.addMenu("IA")

        self.addMenu("Herramientas")

        knowledge_menu = self.addMenu("Base de conocimiento")

        self.save_database = QAction("Guardar base", self)

        self.load_database = QAction("Cargar base", self)

        knowledge_menu.addAction(self.save_database)

        knowledge_menu.addAction(self.load_database)

        self.addMenu("Ayuda")
