# 設計仕様書

## PDF文書自動処理・RAG素材生成ローカルパイプライン

## 1. 文書概要

本設計書は、外部資料 PDF をプロジェクト単位で自動処理し、  
閲覧用・RAG用・機械処理用の成果物を整理して出力するローカル実行型パイプラインの仕様を定義する。

PDF の変換エンジンには `opendataloader-project/opendataloader-pdf` を利用する。  
OpenDataLoader PDF は PDF を **JSON / Markdown / HTML / Text / Annotated PDF** などへ変換でき、Python から `opendataloader_pdf.convert()` で処理できる。ローカル実行を前提としており、文書のレイアウト再構成や RAG への投入しやすさを重視している。 ([github.com](https://github.com/opendataloader-project/opendataloader-pdf?utm_source=openai))

---

## 2. 背景

社内で外部資料を活用する際、以下の課題がある。

- PDF のままでは社内ツールから検索・RAG しづらい
- 文書ごとに構造や品質が異なり、手作業で整理すると負荷が高い
- 処理前後のファイルを人にも機械にも分かりやすく保管したい
- 同じ成果物を、閲覧・RAG・コード連携のそれぞれで再利用したい
- 将来的には Google Drive にアップロードしたいが、まずはローカルで安定して回る仕組みが必要

このため、PDF をローカルで一括処理し、用途別に整理して出力するレポジトリを新規作成する。

---

## 3. 目的

本システムの目的は以下の通り。

1. プロジェクトごとの `01_処理前` フォルダに格納された PDF を自動検出する
2. OpenDataLoader PDF を使って Markdown / JSON / HTML を生成する
3. 処理結果を文書ごとに `02_処理後` へ整理する
4. 人間向け・RAG向け・機械処理向けの成果物を明確に分ける
5. JSON を正本として保持し、将来の再処理や追加活用に耐えられるようにする
6. 将来的な Google Drive アップロードや RAG 基盤連携に拡張しやすくする

---

## 4. スコープ

### 4.1 対象範囲
- ローカル CLI バッチプログラム
- 入力対象は PDF
- プロジェクト単位の一括処理
- Markdown / JSON / HTML の生成
- JSON を用いたチャンク生成
- 用途別ディレクトリへの整理
- README / manifest の自動生成
- 再実行制御（skip / overwrite）

### 4.2 対象外
- Google Drive API 連携
- Web UI
- ベクトルDBへの直接投入
- 権限管理
- OCR 精度の個別調整
- 文書分類や要約などの AI 後処理

---

## 5. 利用者

### 5.1 想定利用者
- 社内業務担当者
- 文書整備担当者
- RAG 基盤利用者
- 開発者

### 5.2 期待される利用形態
- 業務担当者は閲覧用 Markdown / HTML を参照する
- RAG 利用者は chunk JSONL や RAG 用 Markdown を使う
- 開発者は structured JSON や manifest を元に追加ロジックを実装する

---

## 6. 採用技術

- 実装言語: Python 3.10+
- PDF変換エンジン: OpenDataLoader PDF
- ファイル操作: `pathlib`, `shutil`
- JSON処理: Python 標準ライブラリ
- 実行形態: CLI バッチ

OpenDataLoader PDF は Python / Node / Java から利用可能で、Python の `convert()` は複数ファイルやフォルダを処理できる。GitHub README では、`format="json,html,pdf,markdown"` のような複数形式の一括出力例が示されている。 ([github.com](https://github.com/opendataloader-project/opendataloader-pdf?utm_source=openai))

---

## 7. 入出力設計

## 7.1 入力ディレクトリ構成

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

### 入力ルール
- プロジェクトごとにディレクトリを分ける
- 処理対象 PDF は `01_処理前/` に配置する
- PDF 以外のファイルは処理しない

---

## 7.2 出力ディレクトリ構成

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

### 出力思想
- **source.pdf**: 原本参照用
- **01_閲覧用**: 人が読む・確認するための成果物
- **02_RAG用**: RAG や検索処理向けの成果物
- **03_機械処理用**: 再処理・追加ロジック向けの構造化データ

---

## 8. 成果物仕様

## 8.1 閲覧用
### `*.readable.md`
- 人間が内容確認しやすい Markdown
- 文書の読解・レビュー用途

### `*.review.html`
- HTML 形式のレビュー用ファイル
- Markdown より見た目を確認しやすい場合に利用

---

## 8.2 RAG用
### `*.rag.md`
- RAG 処理で利用可能な Markdown
- MVP では `readable.md` と同一内容でも可
- 将来的には RAG 向け正規化版へ分岐可能

### `*.chunks.jsonl`
- 実際のインデックス投入や検索単位となるファイル
- 1 行 1 チャンクの JSONL 形式

### `*.rag_manifest.json`
- RAG 用成果物のメタ情報
- chunk 数、元ファイル、関連ファイルパス等を保持

---

## 8.3 機械処理用
### `*.structured.json`
- OpenDataLoader PDF が生成した構造化 JSON
- 再処理・再 chunk 化・追加ロジックの正本とする

### `*.processing_manifest.json`
- 処理結果のメタ情報
- 入力名、出力先、処理日時等を保持

---

## 9. 機能要件

## 9.1 プロジェクト探索
- 指定ルート配下のプロジェクトディレクトリを列挙する
- `01_処理前` を持つディレクトリのみ対象とする
- `01_処理前/*.pdf` を取得する

### 受け入れ条件
- PDF 以外は無視される
- `01_処理前` がない場合は処理しない

---

## 9.2 PDF変換
- OpenDataLoader PDF を用いて各 PDF を変換する
- 出力形式は最低限 `markdown,json,html` とする

### 受け入れ条件
- `.md`, `.json`, `.html` が生成される
- 変換失敗時は当該文書のみ失敗扱いとする

---

## 9.3 出力整理
- 文書ごとに出力ディレクトリを作成する
- 閲覧用 / RAG用 / 機械処理用ディレクトリを作成する
- 生成ファイルを用途別にリネーム・コピーする

### 受け入れ条件
- 文書ごとに独立した出力構造になる
- ファイル名から用途が分かる

---

## 9.4 チャンク生成
- structured JSON を読み込む
- 見出し・段落・リストを利用して section ベースのチャンクを生成する
- JSONL 形式で保存する

### チャンク最小仕様
```json
{
  "project_id": "PJ-001_案件A",
  "document_id": "要件定義書",
  "chunk_type": "section",
  "heading": "3. セキュリティ要件",
  "text": "本文...",
  "pages": [3, 4],
  "source_pdf": "source.pdf"
}
```

### 受け入れ条件
- `*.chunks.jsonl` が生成される
- 各チャンクに `project_id` と `document_id` が含まれる

---

## 9.5 README / manifest 生成
- 文書フォルダ直下に README を生成する
- RAG manifest / processing manifest を生成する

### README 記載内容
- 各サブフォルダの用途
- `source.pdf` の意味
- どのファイルを人が読むか
- どのファイルを RAG に使うか
- どのファイルをコード連携に使うか

### 受け入れ条件
- 非エンジニアでも用途を理解できる説明が含まれる

---

## 9.6 再実行制御
### `skip`
- 処理済み文書はスキップする

### `overwrite`
- 既存成果物を再生成して上書きする

### 受け入れ条件
- 実行モードを CLI 引数で切り替えられる

---

## 9.7 エラーハンドリング
- 文書単位で例外処理する
- 一部失敗しても他文書の処理は継続する
- 最終的に成功 / 失敗件数を出力する

---

## 10. 非機能要件

## 10.1 可読性
- フォルダ名とファイル名から役割が直感的に理解できること
- 非エンジニアが見ても迷いにくいこと

## 10.2 再現性
- 同じ入力に対して同じ出力構造が生成されること

## 10.3 保守性
- chunk ロジックを差し替えやすいこと
- Google Drive 連携やベクトルDB連携を後付けしやすいこと

## 10.4 拡張性
- 差分更新
- Drive アップロード
- ベクトルDB投入
- RAG用前処理の高度化
などへ拡張可能であること

---

## 11. データ設計

## 11.1 project_id
- プロジェクトディレクトリ名を基本とする
- 例: `PJ-001_案件A`

## 11.2 document_id
- PDFファイル名から拡張子を除いたもの
- 不正文字はサニタイズする

## 11.3 命名規則
- 閲覧用: `*.readable.md`
- RAG用: `*.rag.md`, `*.chunks.jsonl`
- 機械処理用: `*.structured.json`

### 目的
- Drive 外へ移動してもファイル単体で用途が分かるようにする

---

## 12. モジュール設計

```text
pdf-rag-pipeline/
├ src/
│  ├ pipeline/
│  │  ├ main.py
│  │  ├ processor.py
│  │  ├ chunker.py
│  │  ├ manifests.py
│  │  └ naming.py
├ tests/
├ docs/
│  └ design.md
├ README.md
└ TASKS.md
```

### `main.py`
- CLI エントリポイント
- 引数処理
- 全体起動

### `processor.py`
- プロジェクト探索
- PDF探索
- OpenDataLoader 実行
- 出力整理

### `chunker.py`
- structured JSON 読み込み
- section チャンク生成
- JSONL 保存

### `manifests.py`
- README 生成
- manifest 生成

### `naming.py`
- サニタイズ
- ファイル名規則の統一

---

## 13. 処理フロー

```text
ルートディレクトリ入力
  ↓
プロジェクト探索
  ↓
01_処理前 の PDF 列挙
  ↓
一時ディレクトリへ Markdown / JSON / HTML 出力
  ↓
文書ごとに 02_処理後 を構築
  ↓
閲覧用 / RAG用 / 機械処理用 へ整理
  ↓
JSON から chunks.jsonl 生成
  ↓
README / manifest 生成
  ↓
ログ出力して完了
```

---

## 14. 実行仕様

### コマンド例
```bash
python run_pipeline.py workspace/projects
```

### オプション例
```bash
python run_pipeline.py workspace/projects --mode skip
python run_pipeline.py workspace/projects --mode overwrite
```

---

## 15. MVP 定義

### MVP に含める
- CLI 実行
- PDF 検出
- Markdown / JSON / HTML 生成
- 用途別出力ディレクトリ作成
- section ベース chunk 生成
- README / manifest 生成
- skip / overwrite

### MVP に含めない
- Drive アップロード
- ベクトルDB連携
- OCR 高度設定
- UI

---

## 16. 将来拡張

- Google Drive アップロード機能
- 文書差分検知
- ベクトルDB自動投入
- front matter 付き Markdown
- 高度な chunking
- 品質レビュー対象の自動選別
- OpenDataLoader PDF の追加オプション利用

OpenDataLoader PDF は CLI / Python / Node / Java で利用でき、`content_safety_off`、`keep_line_breaks`、`use_struct_tree` などのオプションも用意されているため、将来的な前処理拡張余地がある。 ([github.com](https://github.com/opendataloader-project/opendataloader-pdf?utm_source=openai))

---

## 17. 成功条件

以下を満たした場合、本システムは初期目的を達成したとみなす。

1. `01_処理前` に PDF を置いてコマンド実行すると `02_処理後` が自動生成される
2. 成果物が閲覧用 / RAG用 / 機械処理用に整理される
3. チームメンバーが各ファイル群の用途を直感的に理解できる
4. RAG 用チャンクが JSONL で生成される
5. JSON を正本として残し、将来の再利用に耐えられる
6. 後から Google Drive にアップロードしやすい構成になっている
