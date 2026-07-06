from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

import sys

# Ensure project root is on sys.path when executing this file directly
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Engine.Acquisition.UniversalImporter import UniversalImporter
from Engine.MyChemAI import MyChemAI
from Engine.Logger import Logger



def _safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def document_stats(document: Any) -> Dict[str, Any]:
    raw = getattr(document, "raw", None)

    stats: Dict[str, Any] = {
        "document_id": document.metadata.get("document_id"),
        "name": getattr(document, "name", None),
        "type": getattr(document, "type", None),
        "pages": 0,
        "paragraphs": 0,
        "blocks": 0,
        "lines": 0,
        "spans": 0,
        "headings": 0,
        "sections": 0,
        "images": 0,
        "figures": 0,
        "tables": 0,
        "captions": 0,
        "references": 0,
        "chem_entities": {
            "molecules": _safe_int(len(getattr(document, "molecules", []) or [])),
            "reactions": _safe_int(len(getattr(document, "reactions", []) or [])),
            "spectra": _safe_int(len(getattr(document, "spectra", []) or [])),
        },
        "abbreviations": 0,
    }

    if raw is not None:
        stats["pages"] = _safe_int(len(getattr(raw, "pages", []) or []))
        stats["paragraphs"] = _safe_int(len(getattr(raw, "paragraphs", []) or []))
        stats["blocks"] = _safe_int(sum(len(getattr(p, "blocks", []) or []) for p in getattr(raw, "pages", []) or []))
        stats["lines"] = _safe_int(
            sum(
                sum(len(getattr(b, "lines", []) or []) for b in getattr(p, "blocks", []) or [])
                for p in getattr(raw, "pages", []) or []
            )
        )
        stats["spans"] = _safe_int(len(getattr(raw, "spans", []) or []))
        stats["images"] = _safe_int(len(getattr(raw, "images", []) or []))
        stats["figures"] = _safe_int(len(getattr(raw, "figures", []) or []))
        stats["tables"] = _safe_int(len(getattr(raw, "tables", []) or []))
        stats["references"] = _safe_int(len(getattr(raw, "references", []) or []))

    # Best-effort headings/sections if they exist
    stats["headings"] = _safe_int(len(getattr(raw, "headings", []) or []))
    stats["sections"] = _safe_int(len(getattr(raw, "sections", []) or []))

    return stats


def find_pdfs() -> List[Path]:
    roots = [Path("Engine/Documents/Books"), Path("Engine/Documents/Papers")]
    pdfs: List[Path] = []
    for r in roots:
        if not r.exists():
            continue
        pdfs.extend(list(r.glob("*.pdf")))
    # deterministic order
    pdfs = sorted(pdfs, key=lambda p: p.name)
    return pdfs


def main() -> None:
    importer = UniversalImporter()
    engine = MyChemAI()

    results: List[Dict[str, Any]] = []

    pdfs = find_pdfs()
    Logger.info(f"Validation runner: found {len(pdfs)} PDFs")

    for i, pdf in enumerate(pdfs, start=1):
        Logger.info(f"\n=== [{i}/{len(pdfs)}] Processing: {pdf.name} ===")
        start = time.perf_counter()
        record: Dict[str, Any] = {
            "file": str(pdf),
            "name": pdf.name,
            "ok": False,
            "error": None,
            "time_ms": None,
            "stats": None,
        }

        try:
            # Use the existing workflow to keep backward compatibility
            doc_id = engine.load_document(str(pdf))
            record["ok"] = doc_id is not None
            record["time_ms"] = int((time.perf_counter() - start) * 1000)

            # Fetch the stored document back from engine database
            document = engine.database.documents.get(doc_id)
            if document is None:
                # fallback: we can still compute from intermediate state if needed
                record["stats"] = None
            else:
                record["stats"] = document_stats(document)

            record["error"] = None

            Logger.info(f"Processed: ok={record['ok']} doc_id={doc_id}")

        except Exception as e:
            record["ok"] = False
            record["error"] = str(e)
            record["time_ms"] = int((time.perf_counter() - start) * 1000)
            Logger.info(f"ERROR: {e}")

        results.append(record)

    report_path = Path("validation_report.json")
    report_path.write_text(json.dumps({"results": results}, ensure_ascii=False, indent=2), encoding="utf-8")

    Logger.info(f"\nValidation report written to: {report_path.resolve()}")


if __name__ == "__main__":
    main()

