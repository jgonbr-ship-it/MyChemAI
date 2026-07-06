from pathlib import Path

from Engine.Acquisition.CSVReader import CSVReader
from Engine.Acquisition.PDFReader import PDFReader
from Engine.Acquisition.ImageReader import ImageReader


class UniversalImporter:

    def __init__(self):

        self.readers = {

            ".csv": CSVReader(),

            ".pdf": PDFReader(),

            ".png": ImageReader(),

            ".jpg": ImageReader(),

            ".jpeg": ImageReader(),

            ".bmp": ImageReader(),

            ".tif": ImageReader(),

            ".tiff": ImageReader(),

        }

    def load(self, filepath):

        path = Path(filepath)

        extension = path.suffix.lower()

        if extension not in self.readers:

            raise ValueError(
                f"No existe un Reader para {extension}"
            )

        reader = self.readers[extension]

        print(f"Importador universal usando {reader.__class__.__name__}")

        return reader.load(path)