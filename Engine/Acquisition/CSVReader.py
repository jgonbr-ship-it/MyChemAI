import pandas as pd

from Engine.Acquisition.Reader import Reader


class CSVReader(Reader):

    def load(self, filepath):

        try:

            document = self.create_document(filepath, "CSV")

            df = pd.read_csv(document.path)

            document.tables.append(df)

            print("\nCSV cargado correctamente.")

            return document

        except Exception as e:

            print(e)

            return None