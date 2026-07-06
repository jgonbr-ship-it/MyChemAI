import pandas as pd

from Engine.Acquisition.Reader import Reader
from Engine.Documents.Table import Table, TableCell, TableRow


class CSVReader(Reader):

    def _dataframe_to_table(self, df: pd.DataFrame, page: int = 0) -> Table:
        """Convierte un DataFrame a Engine.Documents.Table.

        Mapeo requerido:
        - columns -> Table.columns
        - rows -> Table.rows
        - cells -> TableCell
        """

        table = Table()
        table.page = page
        table.columns = [str(c) for c in df.columns]

        rows: list[TableRow] = []
        cells: list[TableCell] = []

        # Iterar por filas una sola vez (sin n²)
        for r_idx, (_, row) in enumerate(df.iterrows()):
            row_cells: list[TableCell] = []

            for c_idx, col in enumerate(df.columns):
                value = row[col]
                text = "" if pd.isna(value) else str(value)

                cell = TableCell(text=text, bbox=None, row=r_idx, col=c_idx)
                row_cells.append(cell)
                cells.append(cell)

            rows.append(TableRow(cells=row_cells, bbox=None))

        table.rows = rows
        table.cells = cells

        return table

    def load(self, filepath):

        try:

            document = self.create_document(filepath, "CSV")

            df = pd.read_csv(document.path)

            table = self._dataframe_to_table(df, page=0)

            # Resultado esperado: document.tables SOLO contiene Engine.Documents.Table
            document.tables.append(table)

            # Compatibilidad con extractores/pipeline que usan raw.tables
            document.raw.tables.append(table)

            print("\nCSV cargado correctamente.")

            return document

        except Exception as e:
            print(e)
            return None

