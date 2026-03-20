"""README および manifest ファイルの生成."""

import json
from datetime import datetime, timezone
from pathlib import Path


def generate_rag_manifest(
    project_id: str,
    document_id: str,
    chunk_count: int,
    source_pdf: str,
    output_files: list[str],
) -> dict:
    """RAG用 manifest を生成する."""
    return {
        "project_id": project_id,
        "document_id": document_id,
        "source_pdf": source_pdf,
        "chunk_count": chunk_count,
        "output_files": output_files,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_processing_manifest(
    project_id: str,
    document_id: str,
    source_pdf: str,
    output_files: list[str],
) -> dict:
    """機械処理用 manifest を生成する."""
    return {
        "project_id": project_id,
        "document_id": document_id,
        "source_pdf": source_pdf,
        "output_files": output_files,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }


def write_manifest(manifest: dict, output_path: Path) -> None:
    """manifest を JSON ファイルに書き出す."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")


def generate_readme(document_id: str, source_pdf_name: str) -> str:
    """文書フォルダ用の README.md を生成する."""
    return f"""# {document_id}

このフォルダは **{source_pdf_name}** を自動処理して生成された成果物です。

## フォルダ構成

### `source.pdf`
元の PDF ファイルです。処理結果と原本の対応確認に使います。

### `01_閲覧用/`
人が読む・レビューするための成果物です。

- `{document_id}.readable.md` — 人が読むための Markdown
- `{document_id}.review.html` — HTML 形式の確認用ファイル

### `02_RAG用/`
RAG（検索拡張生成）や検索処理に使う成果物です。

- `{document_id}.rag.md` — RAG 用 Markdown
- `{document_id}.chunks.jsonl` — チャンク単位の投入用データ（1行1チャンク）
- `{document_id}.rag_manifest.json` — RAG 用メタ情報

### `03_機械処理用/`
再処理や追加ロジックで使う構造化データです。

- `{document_id}.structured.json` — 構造化 JSON（正本）
- `{document_id}.processing_manifest.json` — 処理結果のメタ情報
"""


def write_readme(document_id: str, source_pdf_name: str, output_path: Path) -> None:
    """README.md を書き出す."""
    content = generate_readme(document_id, source_pdf_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
