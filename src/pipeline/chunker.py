"""structured JSON からセクションベースのチャンクを生成する."""

import json
from pathlib import Path


def _extract_text_from_element(element: dict) -> str:
    """要素からテキストを再帰的に取得する."""
    parts: list[str] = []
    # opendataloader-pdf は "content" キーを使う; "text" もフォールバック
    text = element.get("content") or element.get("text") or ""
    if text:
        parts.append(text)
    for kid in element.get("kids", []):
        parts.append(_extract_text_from_element(kid))
    return "\n".join(p for p in parts if p)


def _extract_pages_from_element(element: dict) -> list[int]:
    """要素からページ番号を再帰的に収集する."""
    pages: set[int] = set()
    # opendataloader-pdf は "page number" キーを使う; "page" もフォールバック
    page = element.get("page number") or element.get("page")
    if page is not None:
        pages.add(int(page))
    for kid in element.get("kids", []):
        pages.update(_extract_pages_from_element(kid))
    return sorted(pages)


def _walk_sections(elements: list[dict]) -> list[dict]:
    """要素リストを走査し、見出し単位でセクションチャンクにまとめる."""
    chunks: list[dict] = []
    current_heading = ""
    current_texts: list[str] = []
    current_pages: set[int] = set()

    for elem in elements:
        elem_type = elem.get("type", "")
        if elem_type in ("heading", "title"):
            # 前のセクションを確定
            if current_texts:
                chunks.append({
                    "heading": current_heading,
                    "text": "\n".join(current_texts),
                    "pages": sorted(current_pages),
                })
            current_heading = _extract_text_from_element(elem)
            current_texts = []
            current_pages = set()
            current_pages.update(_extract_pages_from_element(elem))
        elif elem_type in ("paragraph", "list", "list_item", "table", "figure_caption"):
            text = _extract_text_from_element(elem)
            if text:
                current_texts.append(text)
            current_pages.update(_extract_pages_from_element(elem))
        # kids を再帰探索
        if "kids" in elem and elem_type not in ("heading", "title"):
            sub_chunks = _walk_sections(elem["kids"])
            if sub_chunks:
                # 手前の蓄積を先に確定
                if current_texts:
                    chunks.append({
                        "heading": current_heading,
                        "text": "\n".join(current_texts),
                        "pages": sorted(current_pages),
                    })
                    current_heading = ""
                    current_texts = []
                    current_pages = set()
                chunks.extend(sub_chunks)

    # 最後のセクション
    if current_texts:
        chunks.append({
            "heading": current_heading,
            "text": "\n".join(current_texts),
            "pages": sorted(current_pages),
        })

    return chunks


def generate_chunks(
    structured_json_path: Path,
    project_id: str,
    document_id: str,
) -> list[dict]:
    """structured.json を読み込み、セクションベースのチャンクを生成する."""
    with open(structured_json_path, encoding="utf-8") as f:
        data = json.load(f)

    # opendataloader-pdf の JSON はトップレベルに kids を持つ
    elements = data.get("kids", [])
    if not elements:
        elements = data.get("elements", [])

    raw_chunks = _walk_sections(elements)

    result = []
    for chunk in raw_chunks:
        result.append({
            "project_id": project_id,
            "document_id": document_id,
            "chunk_type": "section",
            "heading": chunk["heading"],
            "text": chunk["text"],
            "pages": chunk["pages"],
            "source_pdf": "source.pdf",
        })

    return result


def write_chunks_jsonl(chunks: list[dict], output_path: Path) -> None:
    """チャンクリストを JSONL として書き出す."""
    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
