"""chunker モジュールのテスト."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pipeline.chunker import generate_chunks, write_chunks_jsonl


def _write_structured_json(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "test.structured.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return p


class TestGenerateChunks:
    def test_basic_section(self, tmp_path):
        data = {
            "kids": [
                {"type": "heading", "text": "1. はじめに", "page": 1},
                {"type": "paragraph", "text": "本文書の概要です。", "page": 1},
                {"type": "heading", "text": "2. 要件", "page": 2},
                {"type": "paragraph", "text": "要件の詳細。", "page": 2},
            ]
        }
        path = _write_structured_json(tmp_path, data)
        chunks = generate_chunks(path, "PJ-001", "要件定義書")

        assert len(chunks) == 2
        assert chunks[0]["heading"] == "1. はじめに"
        assert chunks[0]["text"] == "本文書の概要です。"
        assert chunks[0]["project_id"] == "PJ-001"
        assert chunks[0]["document_id"] == "要件定義書"
        assert chunks[0]["chunk_type"] == "section"
        assert chunks[0]["source_pdf"] == "source.pdf"
        assert 1 in chunks[0]["pages"]

    def test_empty_json(self, tmp_path):
        data = {"kids": []}
        path = _write_structured_json(tmp_path, data)
        chunks = generate_chunks(path, "PJ-001", "空文書")
        assert chunks == []

    def test_no_heading(self, tmp_path):
        data = {
            "kids": [
                {"type": "paragraph", "text": "見出しなしの段落。", "page": 1},
            ]
        }
        path = _write_structured_json(tmp_path, data)
        chunks = generate_chunks(path, "PJ-001", "test")
        assert len(chunks) == 1
        assert chunks[0]["heading"] == ""
        assert chunks[0]["text"] == "見出しなしの段落。"

    def test_multiple_pages(self, tmp_path):
        data = {
            "kids": [
                {"type": "heading", "text": "章", "page": 1},
                {"type": "paragraph", "text": "1ページ目", "page": 1},
                {"type": "paragraph", "text": "2ページ目", "page": 2},
            ]
        }
        path = _write_structured_json(tmp_path, data)
        chunks = generate_chunks(path, "PJ-001", "test")
        assert len(chunks) == 1
        assert chunks[0]["pages"] == [1, 2]


class TestWriteChunksJsonl:
    def test_write_and_read(self, tmp_path):
        chunks = [
            {"project_id": "PJ-001", "text": "テスト1"},
            {"project_id": "PJ-001", "text": "テスト2"},
        ]
        output = tmp_path / "test.chunks.jsonl"
        write_chunks_jsonl(chunks, output)

        lines = output.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["text"] == "テスト1"
        assert json.loads(lines[1])["text"] == "テスト2"
