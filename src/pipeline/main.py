"""CLI エントリポイント."""

import argparse
import logging
import sys
from pathlib import Path

from .processor import run_pipeline


def setup_logging() -> None:
    """ログ出力を設定する."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 引数をパースする."""
    parser = argparse.ArgumentParser(
        description="PDF RAG Pipeline — PDF を自動処理し RAG 用成果物を生成します",
    )
    parser.add_argument(
        "root",
        type=Path,
        help="プロジェクトルートディレクトリ（workspace/projects 等）",
    )
    parser.add_argument(
        "--mode",
        choices=["skip", "overwrite"],
        default="skip",
        help="再実行制御モード（default: skip）",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """メインエントリポイント."""
    setup_logging()
    args = parse_args(argv)
    logger = logging.getLogger(__name__)

    root = args.root.resolve()
    if not root.is_dir():
        logger.error("指定されたディレクトリが存在しません: %s", root)
        return 1

    logger.info("=== PDF RAG Pipeline 開始 ===")
    logger.info("ルート: %s", root)
    logger.info("モード: %s", args.mode)

    result = run_pipeline(root, mode=args.mode)

    logger.info("=== 処理結果サマリ ===")
    logger.info("  合計: %d 件", result.total)
    logger.info("  成功: %d 件", result.success)
    logger.info("  スキップ: %d 件", result.skipped)
    logger.info("  失敗: %d 件", result.failed)

    if result.failed_docs:
        logger.warning("失敗した文書:")
        for doc in result.failed_docs:
            logger.warning("  - %s", doc)

    return 1 if result.failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
