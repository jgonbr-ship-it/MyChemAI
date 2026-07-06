from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from Engine.Logger import Logger
from Engine.MyChemAI import MyChemAI
from GUI.ConsolePanel import ConsolePanel
from GUI.ExplorerPanel import ExplorerPanel
from GUI.PropertiesPanel import PropertiesPanel
from GUI.StatusPanel import StatusPanel
from GUI.Toolbar import Toolbar
from GUI.Workspace import Workspace


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("MyChemAI")

        self.resize(1600, 900)

        self.engine = MyChemAI()

        self.create_ui()

        self.refresh_database_views()

    def create_ui(self):

        self.toolbar = Toolbar()

        self.setMenuBar(self.toolbar)

        self.setStatusBar(StatusPanel())

        central = QWidget()

        self.setCentralWidget(central)

        main_layout = QVBoxLayout()

        central.setLayout(main_layout)

        top_layout = QHBoxLayout()

        self.explorer = ExplorerPanel()

        self.workspace = Workspace()

        self.properties = PropertiesPanel()

        top_layout.addWidget(self.explorer)

        top_layout.addWidget(self.workspace)

        top_layout.addWidget(self.properties)

        main_layout.addLayout(top_layout)

        self.console = ConsolePanel()

        main_layout.addWidget(self.console)

        Logger.connect_console(self.console)

        self.toolbar.open_csv.triggered.connect(self.open_document)

        self.toolbar.save_database.triggered.connect(self.save_database)

        self.toolbar.load_database.triggered.connect(self.load_database)

    def open_document(self):

        filename, _ = QFileDialog.getOpenFileName(

            self,

            "Seleccionar documento",

            "",

            "Documentos compatibles (*.csv *.pdf *.png *.jpg *.jpeg *.bmp *.tif *.tiff);;Todos los archivos (*)",

        )

        if filename == "":

            return

        Logger.info("")

        Logger.info("=================================")

        Logger.info("Nuevo documento")

        Logger.info("=================================")

        self.engine.load_document(filename)

        self.refresh_database_views()

    def open_csv(self):

        self.open_document()

    def save_database(self):

        filename, _ = QFileDialog.getSaveFileName(

            self,

            "Guardar base de conocimiento",

            str(self.engine.storage.default_path),

            "JSON (*.json)",

        )

        if filename == "":

            return

        self.engine.save_database(filename)

        self.refresh_database_views()

    def load_database(self):

        filename, _ = QFileDialog.getOpenFileName(

            self,

            "Cargar base de conocimiento",

            str(self.engine.storage.default_path),

            "JSON (*.json)",

        )

        if filename == "":

            return

        self.engine.load_database(filename)

        self.refresh_database_views()

    def refresh_database_views(self):

        stats = self.engine.database.statistics()

        storage_path = self.engine.storage.default_path

        self.explorer.show_database_summary(stats)

        self.workspace.show_database_summary(stats)

        self.properties.show_database_details(stats, storage_path)

    def update_explorer(self):

        self.refresh_database_views()
