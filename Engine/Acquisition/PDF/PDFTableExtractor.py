import fitz

import re

from Engine.Documents.Table import Table, TableCell, TableRow


class PDFTableExtractor:

    def extract(self, pdf, document):

        # Real extraction strategy without external deps:
        # - Use PyMuPDF's structured text to approximate rows/cells.
        # - For most chemistry PDFs, tables are often exported as text grids.
        # - We detect table-like blocks by presence of many numeric tokens and separators/newlines.
        for page_number in range(len(pdf)):
            pdf_page = pdf.load_page(page_number)
            page_text_dict = pdf_page.get_text("dict")

            for b in page_text_dict.get("blocks", []):
                bbox = b.get("bbox")
                if not bbox or len(bbox) != 4:
                    continue

                # Candidate table: textual block with many short lines
                lines = b.get("lines", [])
                if len(lines) < 3:
                    continue

                # Create a candidate string grid
                line_texts = []
                for l in lines:
                    parts = []
                    for s in l.get("spans", []):
                        t = s.get("text", "")
                        if t:
                            parts.append(t)
                    lt = "".join(parts).strip()
                    if lt:
                        line_texts.append(lt)

                if len(line_texts) < 3:
                    continue

                numeric_ratio = 0
                total = 0
                for lt in line_texts:
                    tokens = re.findall(r"[0-9]+(?:\.[0-9]+)?%?", lt)
                    if tokens:
                        numeric_ratio += 1
                    total += 1

                if total == 0:
                    continue

                if (numeric_ratio / total) < 0.4:
                    continue

                table = Table()
                table.page = page_number + 1
                table.position = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
                table.bbox = table.position

                # Heuristic cell splitting:
                # - Attempt to split by multiple spaces or tab-like patterns.
                # - If no separators, treat each line as a row with one column.
                rows: list[TableRow] = []
                cells: list[TableCell] = []

                for r_idx, lt in enumerate(line_texts):
                    # choose delimiter
                    parts = [p.strip() for p in re.split(r"\s{2,}|\t+", lt) if p.strip()]
                    if len(parts) <= 1:
                        parts = [lt]

                    row_cells: list[TableCell] = []
                    for c_idx, ct in enumerate(parts):
                        cell = TableCell(text=ct, bbox=None, row=r_idx, col=c_idx)
                        row_cells.append(cell)
                        cells.append(cell)

                    rows.append(TableRow(cells=row_cells, bbox=None))

                table.rows = rows
                table.cells = cells

                # Columns inferred
                max_cols = max((len(r.cells) for r in rows), default=0)
                table.columns = [f"col_{i}" for i in range(max_cols)]

                document.raw.tables.append(table)
                # Keep backward compatibility: document.tables expects a dataframe list; store Table objects there too.
                document.tables.append(table)

        return document
