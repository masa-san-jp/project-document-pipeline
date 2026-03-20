"""naming モジュールのテスト."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pipeline.naming import (
    document_id_from_pdf,
    output_filenames,
    project_id_from_dir,
    sanitize_name,
)


class TestSanitizeName:
    def test_basic(self):
        assert sanitize_name("要件定義書") == "要件定義書"

    def test_removes_invalid_chars(self):
        assert sanitize_name('file<>:"/\\|?*name') == "file_________name"

    def test_strips_dots_and_spaces(self):
        assert sanitize_name("...test...") == "test"

    def test_empty_becomes_underscore(self):
        assert sanitize_name("") == "_"

    def test_only_dots(self):
        assert sanitize_name("...") == "_"

    def test_control_chars(self):
        assert sanitize_name("a\x00b\x1fc") == "a_b_c"


class TestDocumentId:
    def test_basic(self):
        assert document_id_from_pdf(Path("要件定義書.pdf")) == "要件定義書"

    def test_with_special_chars(self):
        result = document_id_from_pdf(Path('test<file>.pdf'))
        assert "<" not in result
        assert ">" not in result


class TestProjectId:
    def test_basic(self):
        assert project_id_from_dir(Path("/workspace/projects/PJ-001_案件A")) == "PJ-001_案件A"


class TestOutputFilenames:
    def test_contains_all_keys(self):
        names = output_filenames("要件定義書")
        assert "readable_md" in names
        assert "review_html" in names
        assert "rag_md" in names
        assert "chunks_jsonl" in names
        assert "rag_manifest" in names
        assert "structured_json" in names
        assert "processing_manifest" in names

    def test_naming_convention(self):
        names = output_filenames("要件定義書")
        assert names["readable_md"] == "要件定義書.readable.md"
        assert names["chunks_jsonl"] == "要件定義書.chunks.jsonl"
        assert names["structured_json"] == "要件定義書.structured.json"
