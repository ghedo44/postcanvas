"""Validate documentation links, assets, examples, and release version consistency."""

from __future__ import annotations

import py_compile
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_FILES = [
    ROOT / "README.md",
    *sorted((ROOT / "docs").rglob("*.md")),
    ROOT / "examples" / "README.md",
]
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_SRC_RE = re.compile(r'''(?:src|href)=["']([^"']+)["']''')
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "data:")


def strip_code_fences(text: str) -> str:
    parts = text.split("```")
    return "".join(part for index, part in enumerate(parts) if index % 2 == 0)


def local_target(source: Path, raw: str) -> Path | None:
    target = raw.strip().split()[0].strip("<>")
    if not target or target.startswith(EXTERNAL_PREFIXES) or target.startswith("#"):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    return (source.parent / target).resolve()


def check_links() -> list[str]:
    errors: list[str] = []
    for markdown in MARKDOWN_FILES:
        if not markdown.exists():
            errors.append(f"missing documentation file: {markdown.relative_to(ROOT)}")
            continue
        text = strip_code_fences(markdown.read_text(encoding="utf-8"))
        refs = LINK_RE.findall(text) + HTML_SRC_RE.findall(text)
        for ref in refs:
            target = local_target(markdown, ref)
            if target is None:
                continue
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{markdown.relative_to(ROOT)}: link escapes repository: {ref}")
                continue
            if not target.exists():
                errors.append(f"{markdown.relative_to(ROOT)}: missing target: {ref}")
    return errors


def check_versions() -> list[str]:
    errors: list[str] = []
    with (ROOT / "pyproject.toml").open("rb") as file:
        version = tomllib.load(file)["project"]["version"]

    init_text = (ROOT / "postcanvas" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)
    if not match:
        errors.append("postcanvas.__version__ is missing")
    elif match.group(1) != version:
        errors.append(f"version mismatch: pyproject={version}, package={match.group(1)}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if f"release-{version.replace('.', '%2E')}" not in readme and f"release-{version}" not in readme:
        errors.append(f"README release badge does not mention {version}")
    return errors


def check_required_docs() -> list[str]:
    required = {
        "docs/getting-started.md",
        "docs/concepts.md",
        "docs/typography.md",
        "docs/rich-text.md",
        "docs/backgrounds-images.md",
        "docs/shapes-effects.md",
        "docs/tables-charts.md",
        "docs/carousels.md",
        "docs/templates.md",
        "docs/validation.md",
        "docs/platform-profiles.md",
        "docs/output-cloud.md",
        "docs/assisted-selection.md",
        "docs/config-reference.md",
        "docs/api-reference.md",
        "docs/renderer-architecture.md",
        "docs/migration-1.0.md",
        "docs/gallery.md",
    }
    return [
        f"missing required guide: {path}"
        for path in sorted(required)
        if not (ROOT / path).exists()
    ]


def compile_examples() -> list[str]:
    errors: list[str] = []
    for source in sorted((ROOT / "examples").glob("*.py")):
        try:
            py_compile.compile(str(source), doraise=True)
        except py_compile.PyCompileError as error:
            errors.append(f"{source.relative_to(ROOT)}: {error.msg}")
    return errors


def main() -> int:
    errors = [*check_links(), *check_versions(), *check_required_docs(), *compile_examples()]
    if errors:
        print("documentation validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"validated {len(MARKDOWN_FILES)} Markdown files")
    print(f"compiled {len(list((ROOT / 'examples').glob('*.py')))} example scripts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
