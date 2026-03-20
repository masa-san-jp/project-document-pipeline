"""プロジェクト探索・PDF変換・成果物振り分け."""

import logging
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from opendataloader_pdf import convert

from .chunker import generate_chunks, write_chunks_jsonl
from .manifests import (
    generate_processing_manifest,
    generate_rag_manifest,
    write_manifest,
    write_readme,
)
from .naming import document_id_from_pdf, output_filenames, project_id_from_dir

logger = logging.getLogger(__name__)

INPUT_DIR_NAME = "01_処理前"
OUTPUT_DIR_NAME = "02_処理後"
VIEWING_DIR = "01_閲覧用"
RAG_DIR = "02_RAG用"
MACHINE_DIR = "03_機械処理用"


@dataclass
class RunResult:
    """パイプライン実行結果."""

    total: int = 0
    success: int = 0
    skipped: int = 0
    failed: int = 0
    failed_docs: list[str] = field(default_factory=list)


def discover_projects(root: Path) -> list[Path]:
    """ルート配下で 01_処理前 を持つプロジェクトディレクトリを列挙する."""
    projects = []
    if not root.is_dir():
        return projects
    for child in sorted(root.iterdir()):
        if child.is_dir() and (child / INPUT_DIR_NAME).is_dir():
            projects.append(child)
    return projects


def discover_pdfs(project_dir: Path) -> list[Path]:
    """プロジェクトの 01_処理前 から PDF 一覧を取得する."""
    input_dir = project_dir / INPUT_DIR_NAME
    if not input_dir.is_dir():
        return []
    return sorted(p for p in input_dir.iterdir() if p.suffix.lower() == ".pdf")


def is_processed(project_dir: Path, doc_id: str) -> bool:
    """文書が処理済みかどうか判定する."""
    doc_dir = project_dir / OUTPUT_DIR_NAME / doc_id
    if not doc_dir.is_dir():
        return False
    names = output_filenames(doc_id)
    structured = doc_dir / MACHINE_DIR / names["structured_json"]
    chunks = doc_dir / RAG_DIR / names["chunks_jsonl"]
    return structured.is_file() and chunks.is_file()


def process_single_pdf(
    pdf_path: Path,
    project_dir: Path,
    project_id: str,
    mode: str,
) -> bool:
    """単一PDFを処理する. 成功時 True を返す."""
    doc_id = document_id_from_pdf(pdf_path)
    names = output_filenames(doc_id)

    if mode == "skip" and is_processed(project_dir, doc_id):
        logger.info("  スキップ: %s（処理済み）", doc_id)
        return True  # skipped は呼び出し側で処理

    logger.info("  処理開始: %s", doc_id)

    doc_output = project_dir / OUTPUT_DIR_NAME / doc_id
    viewing_dir = doc_output / VIEWING_DIR
    rag_dir = doc_output / RAG_DIR
    machine_dir = doc_output / MACHINE_DIR

    for d in [viewing_dir, rag_dir, machine_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. opendataloader-pdf で変換
    with tempfile.TemporaryDirectory() as tmp_dir:
        convert(
            input_path=str(pdf_path),
            output_dir=tmp_dir,
            format="markdown,json,html",
            quiet=True,
        )

        tmp_path = Path(tmp_dir)
        md_files = list(tmp_path.glob("*.md"))
        json_files = list(tmp_path.glob("*.json"))
        html_files = list(tmp_path.glob("*.html"))

        if not md_files or not json_files:
            raise FileNotFoundError(
                f"変換結果が不足しています: md={len(md_files)}, json={len(json_files)}"
            )

        # 2. source.pdf コピー
        shutil.copy2(pdf_path, doc_output / "source.pdf")

        # 3. 閲覧用
        shutil.copy2(md_files[0], viewing_dir / names["readable_md"])
        if html_files:
            shutil.copy2(html_files[0], viewing_dir / names["review_html"])

        # 4. RAG用 Markdown
        shutil.copy2(md_files[0], rag_dir / names["rag_md"])

        # 5. 機械処理用
        shutil.copy2(json_files[0], machine_dir / names["structured_json"])

    # 6. チャンク生成
    structured_path = machine_dir / names["structured_json"]
    chunks = generate_chunks(structured_path, project_id, doc_id)
    write_chunks_jsonl(chunks, rag_dir / names["chunks_jsonl"])

    # 7. manifest 生成
    rag_manifest = generate_rag_manifest(
        project_id=project_id,
        document_id=doc_id,
        chunk_count=len(chunks),
        source_pdf=pdf_path.name,
        output_files=[names["rag_md"], names["chunks_jsonl"]],
    )
    write_manifest(rag_manifest, rag_dir / names["rag_manifest"])

    proc_manifest = generate_processing_manifest(
        project_id=project_id,
        document_id=doc_id,
        source_pdf=pdf_path.name,
        output_files=[names["structured_json"]],
    )
    write_manifest(proc_manifest, machine_dir / names["processing_manifest"])

    # 8. README 生成
    write_readme(doc_id, pdf_path.name, doc_output / "README.md")

    logger.info("  処理完了: %s（%d チャンク生成）", doc_id, len(chunks))
    return True


def run_pipeline(root: Path, mode: str = "skip") -> RunResult:
    """パイプライン全体を実行する."""
    result = RunResult()
    projects = discover_projects(root)

    if not projects:
        logger.warning("処理対象のプロジェクトが見つかりません: %s", root)
        return result

    for project_dir in projects:
        project_id = project_id_from_dir(project_dir)
        pdfs = discover_pdfs(project_dir)

        if not pdfs:
            logger.info("プロジェクト %s: PDF なし", project_id)
            continue

        logger.info("プロジェクト %s: %d 件の PDF を検出", project_id, len(pdfs))

        for pdf_path in pdfs:
            result.total += 1
            doc_id = document_id_from_pdf(pdf_path)

            if mode == "skip" and is_processed(project_dir, doc_id):
                result.skipped += 1
                logger.info("  スキップ: %s（処理済み）", doc_id)
                continue

            try:
                process_single_pdf(pdf_path, project_dir, project_id, mode="overwrite")
                result.success += 1
            except Exception:
                result.failed += 1
                result.failed_docs.append(f"{project_id}/{doc_id}")
                logger.exception("  処理失敗: %s", doc_id)

    return result
