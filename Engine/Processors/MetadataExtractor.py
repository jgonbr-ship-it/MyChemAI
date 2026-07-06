from Engine.Processors.Processor import Processor


class MetadataExtractor(Processor):

    def process(self, document):

        document.metadata["document_type"] = document.type
        document.metadata["source"] = document.source
        document.metadata["path"] = document.path

        if len(document.tables) > 0:

            dataframe = document.tables[0]

            document.metadata["source_columns"] = [
                str(column)
                for column in dataframe.columns
            ]

            document.metadata["row_count"] = int(len(dataframe))

        document.metadata["table_count"] = len(document.tables)
        document.metadata["image_count"] = len(document.images)
        document.metadata["spectrum_count"] = len(document.spectra)

        return document
