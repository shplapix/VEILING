import tokenize
from pathlib import Path


def _scan_frontend_file_for_comments(file_path: Path) -> list[str]:
    content = file_path.read_text(encoding="utf-8")
    violations: list[str] = []
    i = 0
    n = len(content)
    line = 1
    state = "NORMAL"

    while i < n:
        ch = content[i]
        if ch == "\n":
            line += 1
            if state == "LINE_COMMENT":
                state = "NORMAL"
            i += 1
            continue

        if state == "NORMAL":
            if ch == '"':
                state = "DOUBLE_QUOTE"
            elif ch == "'":
                state = "SINGLE_QUOTE"
            elif ch == "`":
                state = "TEMPLATE"
            elif ch == "/" and i + 1 < n and content[i + 1] == "/":
                violations.append(f"{line}: inline single-line comment detected")
                state = "LINE_COMMENT"
                i += 1
            elif ch == "/" and i + 1 < n and content[i + 1] == "*":
                violations.append(f"{line}: block comment detected")
                state = "BLOCK_COMMENT"
                i += 1
        elif state == "DOUBLE_QUOTE":
            if ch == "\\":
                i += 1
            elif ch == '"':
                state = "NORMAL"
        elif state == "SINGLE_QUOTE":
            if ch == "\\":
                i += 1
            elif ch == "'":
                state = "NORMAL"
        elif state == "TEMPLATE":
            if ch == "\\":
                i += 1
            elif ch == "`":
                state = "NORMAL"
            elif ch == "$" and i + 1 < n and content[i + 1] == "{":
                i += 1
        elif state == "BLOCK_COMMENT" and ch == "*" and i + 1 < n and content[i + 1] == "/":
            state = "NORMAL"
            i += 1
        i += 1

    return violations


def test_no_comments_in_python_code() -> None:
    backend_dir = Path(__file__).resolve().parent.parent

    ignored_parts = {".venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
    python_files = [
        f
        for f in backend_dir.rglob("*.py")
        if not any(part in ignored_parts or part.startswith(".") for part in f.parts)
    ]

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
    frontend_dir = root_dir / "frontend"
    if not frontend_dir.exists():
        return

    ignored_dirs = {"node_modules", "dist", ".vite"}
    extensions = {".ts", ".tsx", ".js", ".jsx", ".css"}
    source_files = [
        f
        for f in frontend_dir.rglob("*")
        if f.suffix in extensions and not any(part in ignored_dirs for part in f.parts)
    ]

    violations: list[str] = []
    for file_path in source_files:
        file_violations = _scan_frontend_file_for_comments(file_path)
        for v in file_violations:
            violations.append(f"{file_path.relative_to(root_dir)}:{v}")

    assert not violations, "Frontend comments detected:\n" + "\n".join(violations)


def test_comment_scanner_catches_inline_and_ignores_urls(tmp_path: Path) -> None:
    test_file = tmp_path / "sample.ts"
    test_file.write_text(
        "const x = 10; // an inline comment\n"
        'const url = "https://example.com/api";\n'
        "/* a block comment */\n",
        encoding="utf-8",
    )
    violations = _scan_frontend_file_for_comments(test_file)
    assert len(violations) == 2
    assert "inline single-line comment detected" in violations[0]
    assert "block comment detected" in violations[1]
