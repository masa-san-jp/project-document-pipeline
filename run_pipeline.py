#!/usr/bin/env python3
"""PDF RAG Pipeline のルートエントリポイント."""

import sys
from pathlib import Path

# src/ を import パスに追加
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from pipeline.main import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
