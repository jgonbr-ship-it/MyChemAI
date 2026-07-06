from datetime import datetime

from Engine.Documents.RawContent import RawContent


class Document:

    def __init__(self):

        # ===========================
        # Información básica
        # ===========================

        self.name = None
        self.source = None
        self.type = None
        self.path = None

        # ===========================
        # Fecha de carga
        # ===========================

        self.loaded_at = datetime.now()

        # ===========================
        # Contenido (compatibilidad)
        # ===========================

        self.text = ""
        self.tables = []
        self.images = []

        # ===========================
        # Nuevo contenido estructurado
        # ===========================

        self.raw = RawContent()

        # (Más adelante añadiremos:)
        # self.knowledge = Knowledge()

        # ===========================
        # Conocimiento extraído
        # ===========================

        self.reactions = []
        self.molecules = []
        self.spectra = []
        self.conditions = []

        # ===========================
        # Metadata
        # ===========================

        self.metadata = {}

    def summary(self):

        print("\n========== DOCUMENT ==========")

        print(f"Nombre : {self.name}")
        print(f"Tipo   : {self.type}")
        print(f"Origen : {self.source}")

        print()

        print(f"Texto: {len(self.text)} caracteres")
        print(f"Tablas: {len(self.tables)}")
        print(f"Imágenes: {len(self.images)}")

        print()

        print("Contenido estructurado")

        print(f"Páginas     : {len(self.raw.pages)}")
        print(f"Párrafos    : {len(self.raw.paragraphs)}")
        print(f"Tablas RAW  : {len(self.raw.tables)}")
        print(f"Figuras     : {len(self.raw.figures)}")
        print(f"Imágenes RAW: {len(self.raw.images)}")

        print()

        print("Conocimiento")

        print(f"Reacciones : {len(self.reactions)}")
        print(f"Moléculas  : {len(self.molecules)}")
        print(f"Espectros  : {len(self.spectra)}")
        print(f"Condiciones: {len(self.conditions)}")