
from __future__ import annotations

from datetime import datetime
from pathlib import Path


EXCLUDED_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "env",
    ".mypy_cache",
    ".pytest_cache",
}


def iter_python_files(project_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in project_root.rglob("*.py"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.name.startswith("."):
            continue
        files.append(path)
    return sorted(files)


def iter_project_entries(project_root: Path) -> list[Path]:
    entries: list[Path] = []
    for path in project_root.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.name.startswith("."):
            continue
        entries.append(path)
    return sorted(entries)


def build_tree_text(project_root: Path) -> str:
    entries = iter_project_entries(project_root)
    lines = [f"{project_root.name}/"]
    for path in entries:
        relative = path.relative_to(project_root)
        depth = len(relative.parts) - 1
        indent = "    " * depth
        name = relative.name + ("/" if path.is_dir() else "")
        lines.append(f"{indent}- {name}")
    return "\n".join(lines)


def build_export_text(project_root: Path, files: list[Path]) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tree_text = build_tree_text(project_root)
    lines: list[str] = [
        f"PROJECT ROOT: {project_root}",
        f"GENERATED AT: {generated_at}",
        f"PYTHON FILE COUNT: {len(files)}",
        "",
        "PROJECT TREE:",
        tree_text,
        "",
    ]
    for file_path in files:
        relative_path = file_path.relative_to(project_root)
        content = file_path.read_text(encoding="utf-8")
        lines.extend(
            [
                "=" * 100,
                f"FILE: {relative_path}",
                f"FILENAME: {file_path.name}",
                "=" * 100,
                content.rstrip(),
                "",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    project_root = Path(__file__).resolve().parent
    output_path = project_root / f"{project_root.name}_python_sources.txt"
    files = iter_python_files(project_root)
    export_text = build_export_text(project_root, files)
    output_path.write_text(export_text, encoding="utf-8")
    print(f"Exported {len(files)} Python files to {output_path}")


if __name__ == "__main__":
    main()
