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

                # --- Heurística mejorada para reducir falsos positivos ---
                numeric_lines = 0
                total_lines = 0
                for lt in line_texts:
                    tokens = re.findall(r"[0-9]+(?:\.[0-9]+)?%?", lt)
                    if tokens:
                        numeric_lines += 1
                    total_lines += 1

                if total_lines == 0:
                    continue

                numeric_ratio = numeric_lines / total_lines

                # Reglas: exigir estructura de tabla mínima
                # 1) Evitar bloques tipo índice/listas: demasiado cortos y con baja densidad numérica.
                if numeric_ratio < 0.45:
                    continue

                # 2) Evitar 1-columna: necesitamos que al menos 2 de las primeras filas
                # tengan separación horizontal (múltiples celdas por línea).
                split_rows = []  # list[list[str]]
                for lt in line_texts[:10]:
                    parts = [p.strip() for p in re.split(r"\s{2,}|\t+", lt) if p.strip()]
                    if len(parts) <= 1:
                        # Si no hay separador horizontal fuerte, considerar 1 celda.
                        parts = [lt]
                    split_rows.append(parts)

                # Mínimo 2 columnas reales (en el sentido de múltiple celda por filas)
                max_cols_est = max((len(rp) for rp in split_rows), default=0)
                if max_cols_est < 2:
                    continue

                # Mínimo: al menos 2 filas con >=2 celdas
                multi_cell_rows = sum(1 for rp in split_rows if len(rp) >= 2)
                if multi_cell_rows < 2:
                    continue

                # 3) Evitar bibliografías/índices: si casi todas las líneas son "solo una línea" sin espacios suficientes.
                # (Si todas las líneas tienen patrón de lista/índice, no deberían pasar.)
                # Regla simple: si demasiadas líneas tienen menos de 5 tokens al separar por espacios.
                short_token_lines = 0
                for lt in line_texts[:10]:
                    if len([t for t in re.split(r"\s+", lt.strip()) if t]) < 5:
                        short_token_lines += 1
                if short_token_lines >= 8:
                    continue

                # 4) Mantener varias filas consistentes
                if len(line_texts) < 4:
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

                # Temporal debug: auditoría de tablas (solo logs)
                try:
                    # Primeros 3 valores de la primera fila
                    first_row = rows[0].cells if rows else []
                    first_vals = [c.text for c in first_row[:3]]
                    first_vals_str = " | ".join([str(v) for v in first_vals if v is not None])

                    row_count = len(rows)
                    col_count = max((len(r.cells) for r in rows), default=0)

                    # Motivo por estructura considerada tabla (heurística actual)
                    heuristic_reason = (
                        f"numeric_ratio={numeric_ratio}/{total}; "
                        f"numeric_ratio_ratio={(numeric_ratio/total) if total else 0:.3f}>=0.4; "
                        f"block_bbox=({bbox[0]:.1f},{bbox[1]:.1f},{bbox[2]:.1f},{bbox[3]:.1f}); "
                        f"text_lines={len(line_texts)}"
                    )

                    from Engine.Logger import Logger
                    Logger.info(
                        f"[PDFTableExtractor] page={table.page} rows={row_count} cols={col_count} "
                        f"first_row_vals='{first_vals_str}' reason='{heuristic_reason}'"
                    )
                except Exception:
                    pass

                document.raw.tables.append(table)
                # Keep backward compatibility: document.tables expects a dataframe list; store Table objects there too.
                document.tables.append(table)


        return document
