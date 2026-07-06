from Engine.Acquisition.UniversalImporter import UniversalImporter
from Engine.Classification.DocumentClassifier import DocumentClassifier
from Engine.Intelligence.SchemaDetector import SchemaDetector
from Engine.Interpretation.ReactionParser import ReactionParser
from Engine.Knowledge.KnowledgeBase import KnowledgeBase
from Engine.Logger import Logger
from Engine.Pipeline.PipelineManager import PipelineManager
from Engine.Processors.KnowledgeRegistrationProcessor import KnowledgeRegistrationProcessor
from Engine.Processors.MetadataExtractor import MetadataExtractor
from Engine.Processors.MoleculeExtractor import MoleculeExtractor
from Engine.Processors.ReactionExtractor import ReactionExtractor
from Engine.Processors.SchemaDetectionProcessor import SchemaDetectionProcessor
from Engine.Storage.KnowledgeStorage import KnowledgeStorage


class MyChemAI:

    def __init__(self, auto_load_limit_mb=50):

        Logger.info("Inicializando MyChemAI...")

        self.auto_load_limit_mb = auto_load_limit_mb
        self.auto_save_enabled = True

        self.database = KnowledgeBase()

        self.importer = UniversalImporter()

        self.classifier = DocumentClassifier()

        self.detector = SchemaDetector()

        self.parser = ReactionParser()

        self.storage = KnowledgeStorage()

        self.pipeline = self.create_default_pipeline()

        self.load_database_if_available()

        Logger.info("Motor listo.")

    # ===================================

    def create_default_pipeline(self):

        return PipelineManager(
            [
                SchemaDetectionProcessor(self.detector),
                ReactionExtractor(self.parser),
                MoleculeExtractor(),
                MetadataExtractor(),
                KnowledgeRegistrationProcessor(self.database),
            ]
        )

    # ===================================

    def rebuild_pipeline(self):

        self.pipeline = self.create_default_pipeline()

    # ===================================

    def load_database_if_available(self):

        database_path = self.storage.default_path

        if not self.storage.exists(database_path):

            Logger.info("No hay base persistente previa. Se iniciara una nueva.")

            return

        database_size_mb = database_path.stat().st_size / (1024 * 1024)

        if database_size_mb > self.auto_load_limit_mb:

            Logger.info(
                "Base persistente encontrada, pero no se cargara automaticamente "
                f"porque pesa {database_size_mb:.1f} MB. Puedes cargarla desde "
                "Base de conocimiento > Cargar base."
            )

            self.auto_save_enabled = False

            return

        self.load_database()

    # ===================================

    def load_document(self, filepath):

        Logger.info(f"Cargando documento:\n{filepath}")

        document = self.importer.load(filepath)

        if document is None:

            Logger.info("No se pudo cargar el documento.")

            return None

        initial_classification = self.classifier.classify(document)

        document.metadata["initial_classification"] = initial_classification.to_dict()

        Logger.info(
            "Documento clasificado como "
            f"{initial_classification.document_type}."
        )

        document = self.pipeline.run(document)

        if document is None:

            return None

        final_classification = self.classifier.classify(document)

        document.metadata["classification"] = final_classification.to_dict()

        Logger.info(f"Documento registrado: {document.metadata.get('document_id')}")

        self.log_statistics()

        self.save_database(automatic=True)

        return document.metadata.get("document_id")

    # ===================================

    def load_csv(self, filepath):

        return self.load_document(filepath)

    # ===================================

    def save_database(self, filepath=None, automatic=False):

        if automatic and not self.auto_save_enabled and filepath is None:

            Logger.info(
                "Autoguardado pausado para evitar sobrescribir una base existente "
                "que no fue cargada. Usa Guardar base si quieres escribir un archivo."
            )

            return None

        try:

            path = self.storage.save(self.database, filepath)

            Logger.info(f"Base de conocimiento guardada en:\n{path}")

            return path

        except Exception as error:

            Logger.info(f"No se pudo guardar la base de conocimiento: {error}")

            return None

    # ===================================

    def load_database(self, filepath=None):

        try:

            self.database = self.storage.load(filepath)

            self.rebuild_pipeline()

            self.auto_save_enabled = True

            path = self.storage.resolve_path(filepath)

            Logger.info(f"Base de conocimiento cargada desde:\n{path}")

            self.log_statistics()

            return path

        except Exception as error:

            Logger.info(f"No se pudo cargar la base de conocimiento: {error}")

            return None

    # ===================================

    def log_statistics(self):

        stats = self.database.statistics()

        Logger.info("")

        Logger.info("======= BASE DE CONOCIMIENTO =======")

        Logger.info(f"Documentos : {stats['documents']}")

        Logger.info(f"Reacciones : {stats['reactions']}")

        Logger.info(f"Moleculas  : {stats['molecules']}")

        Logger.info(f"Espectros  : {stats['spectra']}")

        Logger.info("===================================")
