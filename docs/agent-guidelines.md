# Agent Guidelines

Actionable reference for coding agents and contributors working in this repository.

---

## 1. Repository Objectives

- Detect PDFs placed in `01_処理前/` under each project directory
- Convert PDFs to Markdown / JSON / HTML via `opendataloader-pdf`
- Organise outputs under `02_処理後/` into three purpose-specific subdirectories:
  - `01_閲覧用/` — human-readable review files
  - `02_RAG用/` — RAG-ready chunks and manifests
  - `03_機械処理用/` — structured JSON for programmatic reuse
- Generate `chunks.jsonl` from structured JSON (not raw Markdown)
- Auto-generate per-document `README.md` and manifest files
- Run entirely **locally**; Google Drive upload is a future extension

---

## 2. Roles and Permissions

| Role | Responsibility |
|---|---|
| Coding agent | Implement pipeline logic, tests, and docs per design spec |
| Contributor | Add features or fix bugs via feature branches + PRs |
| Reviewer | Approve PRs; verify design conformance and test coverage |

- No secrets or credentials are committed to the repository
- No external API calls are made in the core pipeline (local-only)

---

## 3. Branching Strategy

- **Base branch:** `main`
- **Feature branches:** `feature/<short-description>` (e.g. `feature/add-chunker`, `feature/skip-mode`)
- **Bugfix branches:** `fix/<short-description>`
- **Docs branches:** `docs/<short-description>`
- Branch from `main`; open a PR back to `main`
- Keep branches short-lived; merge and delete after PR is merged

---

## 4. Required Tooling

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Pipeline implementation language |
| Java | 11+ | Required by `opendataloader-pdf` at runtime |
| `opendataloader-pdf` | latest | PDF → Markdown / JSON / HTML conversion engine |
| `pip` | bundled with Python | Package installation |

Verify your environment:

```bash
python --version   # expect 3.10+
java -version      # expect 11+
```

---

## 5. Install Commands

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install the PDF conversion engine
pip install opendataloader-pdf

# Install project dependencies (once requirements.txt exists)
pip install -r requirements.txt
```

---

## 6. Running the Pipeline Locally

```bash
# Basic run — processes all projects under workspace/projects/
python run_pipeline.py workspace/projects

# Skip already-processed documents
python run_pipeline.py workspace/projects --mode skip

# Re-process and overwrite existing outputs
python run_pipeline.py workspace/projects --mode overwrite
```

**Input contract:** place PDF files in `workspace/projects/<PJ-XXX_name>/01_処理前/`

**Expected output tree per document:**

```text
02_処理後/<document-name>/
├── README.md
├── source.pdf
├── 01_閲覧用/
│   ├── <name>.readable.md
│   └── <name>.review.html
├── 02_RAG用/
│   ├── <name>.rag.md
│   ├── <name>.chunks.jsonl
│   └── <name>.rag_manifest.json
└── 03_機械処理用/
    ├── <name>.structured.json
    └── <name>.processing_manifest.json
```

---

## 7. Formatting, Linting, and Testing

> Note: formal tooling is not yet configured. Apply these conventions manually until CI is established.

### Formatting
- Follow [PEP 8](https://peps.python.org/pep-0008/) style
- Use 4-space indentation; no tabs
- Max line length: 120 characters
- When a formatter is added, the expected command will be:
  ```bash
  black src/ tests/
  ```

### Linting
- Avoid unused imports and variables
- When a linter is added, the expected command will be:
  ```bash
  flake8 src/ tests/
  ```

### Testing
- Tests live in `tests/`; mirror the `src/` structure
- Run all tests:
  ```bash
  pytest tests/
  ```
- Run a single test file:
  ```bash
  pytest tests/test_chunker.py -v
  ```
- Minimum coverage targets (once defined): unit tests for `naming.py`, `chunker.py`, `manifests.py`; at least one integration test using a small sample PDF

---

## 8. Commit and PR Conventions

### Commit messages — [Conventional Commits](https://www.conventionalcommits.org/)

```
<type>(<scope>): <short imperative summary>

[optional body]
```

| Type | When to use |
|---|---|
| `feat` | New feature or behavior |
| `fix` | Bug fix |
| `refactor` | Restructure without behavior change |
| `test` | Add or update tests |
| `docs` | Documentation only |
| `chore` | Tooling, deps, CI |

Examples:
```
feat(chunker): add section-based chunk generation
fix(naming): sanitise backslashes in document IDs
docs(agent-guidelines): add branching strategy section
```

### Pull Request conventions
- **Keep PRs small and focused** — one logical change per PR
- Title follows the same Conventional Commits format as above
- Description must include:
  - **What changed** (bullet list)
  - **Before / After** notes (e.g. output structure, behavior, CLI flags)
  - Link to related issue or task if applicable
- All automated checks must pass before requesting review
- At least one reviewer approval required before merging

---

## 9. Review Checklist

Before approving a PR, verify:

- [ ] Code follows PEP 8 and the 120-char line limit
- [ ] No hardcoded paths, project IDs, or document IDs
- [ ] New modules have corresponding tests in `tests/`
- [ ] `chunks.jsonl` rows include `project_id` and `document_id`
- [ ] File naming follows the `readable / rag / structured` convention
- [ ] Existing tests still pass (`pytest tests/`)
- [ ] PR description includes Before / After notes
- [ ] No credentials, API keys, or personal data committed
- [ ] `docs/design.md` updated if the design spec changed

---

## 10. Runbook — Common Tasks

### Add a new output processor

1. Create `src/pipeline/<processor_name>.py`
2. Implement a function with signature:
   ```python
   def process(doc_dir: Path, doc_json: dict, project_id: str, document_id: str) -> None:
       ...
   ```
3. Call it from `src/pipeline/processor.py` after the existing output-arrangement step
4. Add tests in `tests/test_<processor_name>.py`
5. Update `docs/design.md` → section 8 (成果物仕様) with the new output file description

### Adjust chunking strategy

1. Edit `src/pipeline/chunker.py` (or `chunker.py` in the root until `src/` is scaffolded)
2. Locate `chunk_by_section()` (or equivalent)
3. Modify the element-traversal or merge logic
4. Update or add unit tests in `tests/test_chunker.py` covering the changed behavior
5. Run:
   ```bash
   pytest tests/test_chunker.py -v
   ```
6. Note the Before / After chunk schema in the PR description

### Add new manifest fields

1. Open `src/pipeline/manifests.py`
2. Add the new key–value pair(s) to the relevant manifest dict (`rag_manifest` or `processing_manifest`)
3. Update `docs/design.md` → section 8.2 or 8.3 with the new field definition
4. Update or add tests in `tests/test_manifests.py`
5. Include a Before / After JSON snippet in the PR description

### Add a new CLI option

1. Edit the argument parser in `src/pipeline/main.py` (or `run_pipeline.py`)
2. Add the argument with `argparse.add_argument()`
3. Thread the value through to the relevant function
4. Document the option in this file under **Section 6** and in `README.md`
5. Add a test that invokes the CLI with the new flag

---

## 11. Key Design Decisions (quick reference)

- **JSON is the canonical output** — never discard `structured.json`; all chunk generation reads from it
- **`chunks.jsonl` is the RAG primary** — do not use raw Markdown as the sole RAG input
- **One `convert()` call per batch** — avoid per-file JVM restarts; pass a list of paths to `opendataloader_pdf.convert()`
- **File naming carries intent** — `*.readable.md`, `*.rag.md`, `*.chunks.jsonl`, `*.structured.json` must be used verbatim
- **Error isolation** — a single document failure must not abort the entire run; log and continue
