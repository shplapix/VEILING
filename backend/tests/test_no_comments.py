import re
import tokenize
from pathlib import Path


def test_no_comments_in_python_code() -> None:
    backend_dir = Path(__file__).resolve().parent.parent
    app_dir = backend_dir / "app"
    tests_dir = backend_dir / "tests"

    python_files: list[Path] = []
    for directory in (app_dir, tests_dir):
        if directory.exists():
            python_files.extend(directory.rglob("*.py"))

    violations: list[str] = []
    for file_path in python_files:
        with file_path.open("rb") as f:
            try:
                tokens = tokenize.tokenize(f.readline)
                for tok in tokens:
                    if tok.type == tokenize.COMMENT:
                        violations.append(
                            f"{file_path.relative_to(backend_dir)}:{tok.start[0]}: {tok.string}"
                        )
            except tokenize.TokenError:
                violations.append(f"{file_path.relative_to(backend_dir)}: TokenError during scan")

    assert not violations, "Python comments detected:\n" + "\n".join(violations)


def test_no_comments_in_frontend_code() -> None:
    root_dir = Path(__file__).resolve().parent.parent.parent
    frontend_src = root_dir / "frontend" / "src"
    if not frontend_src.exists():
        return

    source_files = [
        f for f in frontend_src.rglob("*") if f.suffix in {".ts", ".tsx", ".js", ".jsx", ".css"}
    ]

    single_line_regex = re.compile(r"^\s*//")
    block_comment_start = re.compile(r"/\*")

    violations: list[str] = []
    for file_path in source_files:
        lines = file_path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, start=1):
            if single_line_regex.search(line) or block_comment_start.search(line):
                violations.append(f"{file_path.relative_to(root_dir)}:{idx}: {line.strip()}")

    assert not violations, "Frontend comments detected:\n" + "\n".join(violations)
