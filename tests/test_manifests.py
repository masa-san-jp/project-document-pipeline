"""manifests モジュールのテスト."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pipeline.manifests import (
    generate_processing_manifest,
    generate_rag_manifest,
    generate_readme,
    write_manifest,
    write_readme,
)


class TestRagManifest:
    def test_basic(self):
        m = generate_rag_manifest(
            project_id="PJ-001",
            document_id="要件定義書",
            chunk_count=10,
            source_pdf="要件定義書.pdf",
            output_files=["要件定義書.rag.md", "要件定義書.chunks.jsonl"],
        )
        assert m["project_id"] == "PJ-001"
        assert m["document_id"] == "要件定義書"
        assert m["chunk_count"] == 10
        assert "processed_at" in m


class TestProcessingManifest:
    def test_basic(self):
        m = generate_processing_manifest(
            project_id="PJ-001",
            document_id="要件定義書",
            source_pdf="要件定義書.pdf",
            output_files=["要件定義書.structured.json"],
        )
        assert m["project_id"] == "PJ-001"
        assert m["source_pdf"] == "要件定義書.pdf"
        assert "processed_at" in m


class TestWriteManifest:
    def test_round_trip(self, tmp_path):
        m = {"project_id": "PJ-001", "test": True}
        output = tmp_path / "test.json"
        write_manifest(m, output)
        loaded = json.loads(output.read_text(encoding="utf-8"))
        assert loaded == m


class TestReadme:
    def test_contains_key_sections(self):
        content = generate_readme("要件定義書", "要件定義書.pdf")
        assert "# 要件定義書" in content
        assert "source.pdf" in content
        assert "01_閲覧用" in content
        assert "02_RAG用" in content
        assert "03_機械処理用" in content
        assert "readable.md" in content
        assert "chunks.jsonl" in content
        assert "structured.json" in content

    def test_write_readme(self, tmp_path):
        output = tmp_path / "README.md"
        write_readme("テスト文書", "テスト文書.pdf", output)
        content = output.read_text(encoding="utf-8")
        assert "# テスト文書" in content
