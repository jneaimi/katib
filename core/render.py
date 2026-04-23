"""PDF rendering via WeasyPrint.

Thin wrapper that takes an HTML string + optional base URL (for resolving
relative asset paths like logos and images) and writes a PDF.

Phase 1: single-PDF output only. Multi-PDF composition (merging, page
range selection, cover + body splicing) is a Phase 2+ concern if needed.
"""
from __future__ import annotations

from pathlib import Path

from weasyprint import HTML


def render_to_pdf(
    html_str: str,
    out_path: Path | str,
    base_url: Path | str | None = None,
) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    base = str(base_url) if base_url else None
    HTML(string=html_str, base_url=base).write_pdf(str(out))
    return out
