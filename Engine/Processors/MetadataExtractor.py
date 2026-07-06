from Engine.Processors.Processor import Processor


class MetadataExtractor(Processor):

    def process(self, document):

        document.metadata["document_type"] = document.type
        document.metadata["source"] = document.source
        document.metadata["path"] = document.path

        # document.tables puede contener distintos tipos según el Reader.
        # Requisito: evitar dependencia de pandas y soportar Engine.Documents.Table.
        if len(document.tables) > 0:

            table0 = document.tables[0]

            # Caso: Engine.Documents.Table
            if hasattr(table0, "columns") and hasattr(table0, "rows"):

                try:
                    document.metadata["source_columns"] = [
                        str(c) for c in (table0.columns or [])
                    ]
                except Exception:
                    document.metadata["source_columns"] = []

                try:
                    document.metadata["row_count"] = int(len(getattr(table0, "rows", [])))
                except Exception:
                    document.metadata["row_count"] = 0

            # Caso legado (posible): pandas.DataFrame
            elif hasattr(table0, "columns"):

                try:
                    document.metadata["source_columns"] = [
                        str(column) for column in table0.columns
                    ]
                except Exception:
                    document.metadata["source_columns"] = []

                try:
                    document.metadata["row_count"] = int(len(table0))
                except Exception:
                    document.metadata["row_count"] = 0

            else:
                # No lanzar excepciones por tipos incompatibles.
                document.metadata["source_columns"] = []
                document.metadata["row_count"] = 0


        document.metadata["table_count"] = len(document.tables)
        document.metadata["image_count"] = len(document.images)
        document.metadata["spectrum_count"] = len(document.spectra)

        return document
