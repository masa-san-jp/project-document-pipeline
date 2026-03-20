# PDF RAG Pipeline

プロジェクト単位で `01_処理前` フォルダに格納した PDF を自動処理し、  
`02_処理後` に以下の用途別成果物を生成するローカルバッチです。

- **閲覧用**: 人が読む・確認するためのファイル
- **RAG用**: 社内RAGや検索インデックス投入用のファイル
- **機械処理用**: 再処理や追加ロジックで使う構造化データ

PDFの解析・変換には [`opendataloader-project/opendataloader-pdf`](https://github.com/opendataloader-project/opendataloader-pdf) を利用します。

---

## 目的

このレポジトリの目的は、外部資料 PDF をプロジェクトごとに整理しながら、

1. 人間が確認しやすい成果物を作る
2. RAGに投入しやすい形式へ変換する
3. JSONベースの再利用可能な構造化データを保持する

ことです。

将来的には Google Drive へアップロードすることを想定していますが、  
まずは **ローカルで完結する再現可能な処理パイプライン** として実装します。

---

## 想定ユースケース

- プロジェクトごとに複数の外部資料を保管・処理したい
- PDFを Markdown 化して社内ツールから RAG したい
- 処理前後ファイルを人にもわかりやすく整理したい
- 将来 Google Drive にそのままアップロードできる構造で出力したい
- JSON を残して将来の再処理やコード連携にも使いたい

---

## ディレクトリ構成

### 入力

```text
workspace/
└ projects/
   ├ PJ-001_案件A/
   │  ├ 01_処理前/
   │  │  ├ 要件定義書.pdf
   │  │  └ 提案資料.pdf
   │  └ 02_処理後/
   └ PJ-002_案件B/
      ├ 01_処理前/
      └ 02_処理後/
```

### 出力

```text
02_処理後/
└ 要件定義書/
   ├ README.md
   ├ source.pdf
   ├ 01_閲覧用/
   │  ├ 要件定義書.readable.md
   │  └ 要件定義書.review.html
   ├ 02_RAG用/
   │  ├ 要件定義書.rag.md
   │  ├ 要件定義書.chunks.jsonl
   │  └ 要件定義書.rag_manifest.json
   └ 03_機械処理用/
      ├ 要件定義書.structured.json
      └ 要件定義書.processing_manifest.json
```

---

## 各成果物の役割

### `source.pdf`
元のPDFです。処理結果と原本の対応をすぐ確認できるよう、文書ごとの出力フォルダにも配置します。

### `01_閲覧用/`
人が読む・レビューするための成果物です。

- `*.readable.md`: 人が読むための Markdown
- `*.review.html`: HTML 形式の確認用ファイル

### `02_RAG用/`
RAG や検索処理に使う成果物です。

- `*.rag.md`: RAG用 Markdown
- `*.chunks.jsonl`: チャンク単位の投入用データ
- `*.rag_manifest.json`: RAG用メタ情報

### `03_機械処理用/`
再処理や追加実装で使う構造化データです。

- `*.structured.json`: `opendataloader-pdf` の構造化出力
- `*.processing_manifest.json`: 処理結果のメタ情報

---

## 処理フロー

1. `projects/*/01_処理前/` 内の PDF を検出
2. `opendataloader-pdf` で Markdown / JSON / HTML を生成
3. `02_処理後/<文書名>/` を作成
4. 用途別に成果物を配置
5. JSON から RAG 用チャンクを生成
6. README / manifest を生成

---

## 技術方針

- 実装言語: Python
- PDF変換: `opendataloader-pdf`
- 実行方式: ローカルCLIバッチ
- 出力の正本: JSON
- RAG用チャンク生成元: JSON
- Google Drive連携: 将来拡張

---

## なぜ Markdown だけでなく JSON も残すのか

Markdown は人間が確認しやすく、RAG の前段でも使いやすい形式です。  
一方で、将来的な再利用やチャンク戦略の見直し、ページ情報・構造情報の保持には JSON が必要です。

そのため本レポジトリでは、

- **Markdown**: 人が読む / 軽量に使う
- **JSON**: 構造化データの正本
- **chunks.jsonl**: RAG投入用の派生データ

という扱いにします。

---

## 実行イメージ

```bash
python run_pipeline.py workspace/projects
```

オプション例:

```bash
python run_pipeline.py workspace/projects --mode skip
python run_pipeline.py workspace/projects --mode overwrite
```

- `skip`: 既に処理済みの文書はスキップ
- `overwrite`: 再生成して上書き

---

## MVP 範囲

- `01_処理前` の PDF 検出
- Markdown / JSON / HTML 生成
- `02_処理後` の用途別整理
- RAG用チャンク生成
- README / manifest 生成
- skip / overwrite モード

---

## 将来拡張

- Google Drive への自動アップロード
- 差分更新
- ベクトルDB連携
- OCR強化・複雑PDF向けモード切替
- 品質レビュー対象の自動抽出

---

## 依存関係

- Python 3.10+
- Java 11+（`opendataloader-pdf` 利用要件に応じて必要）
- `opendataloader-pdf`

---

## 開発方針

- ファイル名から用途がわかること
- 非エンジニアでも構造を理解できること
- JSON を捨てず、再利用可能性を維持すること
- ローカルで完結して再現可能であること
- 将来 Drive や RAG 基盤へ拡張しやすいこと

---

## 補足

このレポジトリは、`opendataloader-pdf` をそのまま使うものではなく、  
それを **PDF変換エンジンとして利用するラッパーパイプライン** です。

変換後ファイルの整理、命名、README/manifest 生成、チャンク生成は本レポジトリ側で実装します。

---

## コントリビューター・エージェント向けガイドライン

ブランチ戦略・ツール要件・コミット規約・レビューチェックリスト・よくある作業のランブックは、  
**[docs/agent-guidelines.md](docs/agent-guidelines.md)** を参照してください。
