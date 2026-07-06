import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is on sys.path so `Engine` can be imported when running as:
#   python Tests/e2e_validation.py ...
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Engine.MyChemAI import MyChemAI


@dataclass
class TestResult:
    path: str
    ok: bool
    duration_s: float
    doc_id: Optional[str]
    metrics: Dict[str, Any]
    exception: Optional[str]


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def format_duration(seconds: float) -> str:
    return f"{seconds:.3f}s"


def iter_pdf_files(target: Path) -> List[Path]:
    """
    target:
      - file ending with .pdf -> [file]
      - directory -> all .pdf recursively
    """
    if target.is_file():
        if target.suffix.lower() != ".pdf":
            return []
        return [target]

    if target.is_dir():
        return sorted([p for p in target.rglob("*.pdf") if p.is_file()])

    return []


def get_metrics(engine: MyChemAI, doc_id: Optional[str]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Extract metrics from the Document stored in engine.database.documents.
    Keep extraction resilient to missing attributes for backward compatibility.
    """
    document_obj = engine.database.documents.get(doc_id) if doc_id is not None else None

    raw_pages = getattr(getattr(document_obj, "raw", None), "pages", []) if document_obj is not None else []
    raw_paragraphs = getattr(getattr(document_obj, "raw", None), "paragraphs", []) if document_obj is not None else []
    raw_figures = getattr(getattr(document_obj, "raw", None), "figures", []) if document_obj is not None else []
    raw_images = getattr(getattr(document_obj, "raw", None), "images", []) if document_obj is not None else []
    raw_references = getattr(getattr(document_obj, "raw", None), "references", []) if document_obj is not None else []
    raw_sections = getattr(getattr(document_obj, "raw", None), "sections", []) if document_obj is not None else []
    raw_chapters = getattr(getattr(document_obj, "raw", None), "chapters", []) if document_obj is not None else []

    # Fallback: document-level lists
    tables = getattr(document_obj, "tables", []) if document_obj is not None else []
    images = getattr(document_obj, "images", []) if document_obj is not None else []
    molecules = getattr(document_obj, "molecules", []) if document_obj is not None else []
    reactions = getattr(document_obj, "reactions", []) if document_obj is not None else []

    # Requested: blocks, lines, spans, captions, references
    # Current pipeline stores:
    # - blocks/lines/spans not explicitly persisted; derive best-effort counts from Paragraphs/Sentences.
    # - references/figures/captions: currently in RawContent lists but may be empty.
    paragraphs_count = safe_int(len(raw_paragraphs))
    pages_count = safe_int(len(raw_pages))

    # Lines/spans/blocks: best-effort estimates based on available structure.
    # If Paragraph has sentences, those act as lines-ish units; spans not available.
    sentences_count = 0
    for par in raw_paragraphs:
        sentences = getattr(par, "sentences", None)
        if sentences is not None:
            sentences_count += len(sentences)

    blocks_count = paragraphs_count  # conservative proxy
    lines_count = sentences_count   # best-effort proxy for "líneas"
    spans_count = 0                  # not currently persisted by PDFTextExtractor

    # Captions: no concrete extraction in current code; proxy from references/figures count.
    captions_count = 0
    if len(raw_figures) > 0:
        captions_count = safe_int(len(raw_figures))

    schema = getattr(document_obj, "metadata", {}).get("schema", {}) if document_obj is not None else {}
    schema_keys = sorted(list(schema.keys())) if isinstance(schema, dict) else []

    metrics: Dict[str, Any] = {
        "name": getattr(document_obj, "name", None) if document_obj is not None else None,
        "pages": pages_count,
        "blocks": blocks_count,
        "lines": lines_count,
        "spans": spans_count,
        "paragraphs": paragraphs_count,
        "tables": safe_int(len(tables)),
        "images": safe_int(len(images) if isinstance(images, list) else len(raw_images)),
        "references": safe_int(len(raw_references)),
        "captions": safe_int(captions_count),
        "molecules": safe_int(len(molecules)),
        "reactions": safe_int(len(reactions)),
        "schema_keys": schema_keys,
        "chapters": safe_int(len(raw_chapters)),
        "sections": safe_int(len(raw_sections)),
    }
    return metrics, schema_keys


def run_document(engine: MyChemAI, pdf_path: Path) -> TestResult:
    started = time.perf_counter()
    doc_id: Optional[str] = None

    try:
        document_id = engine.load_document(str(pdf_path))
        doc_id = document_id

        metrics, _ = get_metrics(engine, doc_id)
        duration = time.perf_counter() - started

        # Print per-PDF requested output
        print(f"\n=== {pdf_path.name} ===")
        print(f"pages: {metrics.get('pages')}")
        print(f"blocks: {metrics.get('blocks')}")
        print(f"lines: {metrics.get('lines')}")
        print(f"spans: {metrics.get('spans')}")
        print(f"paragraphs: {metrics.get('paragraphs')}")
        print(f"tables: {metrics.get('tables')}")
        print(f"images: {metrics.get('images')}")
        print(f"references: {metrics.get('references')}")
        print(f"captions: {metrics.get('captions')}")
        print(f"molecules: {metrics.get('molecules')}")
        print(f"reactions: {metrics.get('reactions')}")
        print(f"time: {format_duration(duration)}")
        print(f"schema_keys: {metrics.get('schema_keys')}")

        return TestResult(
            path=str(pdf_path),
            ok=True,
            duration_s=duration,
            doc_id=doc_id,
            metrics=metrics,
            exception=None,
        )

    except Exception as e:
        duration = time.perf_counter() - started
        print(f"\n=== {pdf_path.name} ===")
        print(f"[FAIL] {type(e).__name__}: {e}")
        print(f"time: {format_duration(duration)}")

        return TestResult(
            path=str(pdf_path),
            ok=False,
            duration_s=duration,
            doc_id=doc_id,
            metrics={},
            exception=f"{type(e).__name__}: {e}",
        )


def print_usage() -> None:
    script = Path(sys.argv[0]).name
    print("\nUsage:")
    print(f"  python {script} \"C:\\Libros\\Atkins.pdf\"")
    print(f"  python {script} \"C:\\Libros\"")
    print("")
    print("Behavior:")
    print("- If argument is a .pdf -> process it")
    print("- If argument is a directory -> recursively process all .pdf files")
    print("- If no argument is given -> show this help")


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print_usage()
        return 2

    targets: List[Path] = []
    for arg in argv[1:]:
        targets.append(Path(arg))

    pdfs: List[Path] = []
    for t in targets:
        pdfs.extend(iter_pdf_files(t))

    # Deduplicate while preserving order
    seen = set()
    unique_pdfs: List[Path] = []
    for p in pdfs:
        if str(p) not in seen:
            seen.add(str(p))
            unique_pdfs.append(p)

    if not unique_pdfs:
        print("No .pdf files found for given argument(s).")
        return 2

    engine = MyChemAI()
    results: List[TestResult] = []

    start_all = time.perf_counter()

    for pdf in unique_pdfs:
        # Never stop: continue on failure
        res = run_document(engine, pdf)
        results.append(res)

    total_time = time.perf_counter() - start_all
    processed = len(results)
    successful = sum(1 for r in results if r.ok)
    failed = processed - successful
    avg_time = (total_time / processed) if processed else 0.0

    print("\n==============================")
    print("SUMMARY")
    print("==============================")
    print(f"pdfs procesados: {processed}")
    print(f"exitosos: {successful}")
    print(f"fallidos: {failed}")
    print(f"tiempo total: {format_duration(total_time)}")
    print(f"promedio por documento: {format_duration(avg_time)}")
    print("==============================")

    # exit code: 0 if all passed, 1 otherwise
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
