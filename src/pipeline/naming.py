"""ファイル命名・サニタイズユーティリティ."""

import re
from pathlib import Path

# OS依存で使えない文字
_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize_name(name: str) -> str:
    """ファイル名に使えない文字を除去・置換する."""
    sanitized = _INVALID_CHARS.sub("_", name)
    sanitized = sanitized.strip(". ")
    if not sanitized:
        sanitized = "_"
    return sanitized


def document_id_from_pdf(pdf_path: Path) -> str:
    """PDFファイル名から拡張子を除いた document_id を返す."""
    return sanitize_name(pdf_path.stem)


def project_id_from_dir(project_dir: Path) -> str:
    """プロジェクトディレクトリ名を project_id として返す."""
    return project_dir.name


def output_filenames(doc_id: str) -> dict[str, str]:
    """文書IDから各成果物のファイル名を生成する."""
    return {
        "readable_md": f"{doc_id}.readable.md",
        "review_html": f"{doc_id}.review.html",
        "rag_md": f"{doc_id}.rag.md",
        "chunks_jsonl": f"{doc_id}.chunks.jsonl",
        "rag_manifest": f"{doc_id}.rag_manifest.json",
        "structured_json": f"{doc_id}.structured.json",
        "processing_manifest": f"{doc_id}.processing_manifest.json",
    }
