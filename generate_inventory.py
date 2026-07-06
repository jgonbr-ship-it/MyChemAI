from pathlib import Path
import ast

ROOT = Path(__file__).parent
OUTPUT = ROOT / "PROJECT_INVENTORY.md"

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "Database",
    "Engine/Documents/Books",
    "Engine/Documents/Papers",
}

IGNORE_EXT = {
    ".pyc",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
    ".zip",
    ".json",
}


def ignored(path: Path):
    p = path.as_posix()
    for d in IGNORE_DIRS:
        if p == d or p.startswith(d + "/"):
            return True
    return False


with open(OUTPUT, "w", encoding="utf8") as out:

    out.write("# PROJECT INVENTORY\n\n")

    out.write("## DIRECTORY TREE\n\n")

    for item in sorted(ROOT.rglob("*")):

        if ignored(item):
            continue

        if item.suffix.lower() in IGNORE_EXT:
            continue

        depth = len(item.relative_to(ROOT).parts)

        out.write("    " * (depth - 1))

        if item.is_dir():
            out.write(f"📁 {item.name}\n")
        else:
            out.write(f"📄 {item.name}\n")

    out.write("\n\n")

    out.write("# PYTHON FILES\n")

    for py in sorted(ROOT.rglob("*.py")):

        if ignored(py):
            continue

        out.write("\n")
        out.write("=" * 80 + "\n")
        out.write(py.relative_to(ROOT).as_posix() + "\n")
        out.write("=" * 80 + "\n\n")

        try:

            source = py.read_text(encoding="utf8")

            tree = ast.parse(source)

            imports = []

            classes = []

            functions = []

            for node in tree.body:

                if isinstance(node, ast.Import):

                    for n in node.names:
                        imports.append(n.name)

                elif isinstance(node, ast.ImportFrom):

                    module = node.module or ""

                    for n in node.names:
                        imports.append(f"{module}.{n.name}")

                elif isinstance(node, ast.ClassDef):

                    methods = []

                    for item in node.body:

                        if isinstance(item, ast.FunctionDef):

                            methods.append(item.name)

                    classes.append((node.name, methods))

                elif isinstance(node, ast.FunctionDef):

                    functions.append(node.name)

            out.write("Imports:\n")

            for i in imports:
                out.write(f"  - {i}\n")

            out.write("\n")

            out.write("Classes:\n")

            for cls, methods in classes:

                out.write(f"\n  {cls}\n")

                for m in methods:
                    out.write(f"      - {m}\n")

            out.write("\n")

            out.write("Functions:\n")

            for f in functions:
                out.write(f"  - {f}\n")

            out.write("\n")

        except Exception as e:

            out.write(f"ERROR: {e}\n\n")

print()
print("=" * 70)
print("PROJECT_INVENTORY.md generado correctamente.")
print("=" * 70)