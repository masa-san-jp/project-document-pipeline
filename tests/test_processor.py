"""processor モジュールのテスト."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pipeline.processor import discover_pdfs, discover_projects, is_processed


class TestDiscoverProjects:
    def test_finds_projects_with_input_dir(self, tmp_path):
        pj1 = tmp_path / "PJ-001_案件A"
        (pj1 / "01_処理前").mkdir(parents=True)
        pj2 = tmp_path / "PJ-002_案件B"
        (pj2 / "01_処理前").mkdir(parents=True)
        # プロジェクトでないディレクトリ
        (tmp_path / "other").mkdir()

        projects = discover_projects(tmp_path)
        assert len(projects) == 2
        assert pj1 in projects
        assert pj2 in projects

    def test_empty_root(self, tmp_path):
        assert discover_projects(tmp_path) == []

    def test_nonexistent_root(self):
        assert discover_projects(Path("/nonexistent")) == []


class TestDiscoverPdfs:
    def test_finds_pdfs(self, tmp_path):
        pj = tmp_path / "PJ-001"
        input_dir = pj / "01_処理前"
        input_dir.mkdir(parents=True)
        (input_dir / "doc1.pdf").write_text("dummy")
        (input_dir / "doc2.pdf").write_text("dummy")
        (input_dir / "notes.txt").write_text("dummy")

        pdfs = discover_pdfs(pj)
        assert len(pdfs) == 2
        assert all(p.suffix == ".pdf" for p in pdfs)

    def test_no_input_dir(self, tmp_path):
        pj = tmp_path / "PJ-001"
        pj.mkdir()
        assert discover_pdfs(pj) == []


class TestIsProcessed:
    def test_not_processed(self, tmp_path):
        assert is_processed(tmp_path, "doc1") is False

    def test_processed(self, tmp_path):
        doc_dir = tmp_path / "02_処理後" / "doc1"
        machine_dir = doc_dir / "03_機械処理用"
        rag_dir = doc_dir / "02_RAG用"
        machine_dir.mkdir(parents=True)
        rag_dir.mkdir(parents=True)
        (machine_dir / "doc1.structured.json").write_text("{}")
        (rag_dir / "doc1.chunks.jsonl").write_text("")
        assert is_processed(tmp_path, "doc1") is True
