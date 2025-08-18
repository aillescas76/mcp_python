# MCP Python Code Navigation Server — Detailed Implementation Plan

This plan breaks the project into clear, verifiable tasks suitable for junior developers. Each task includes goals, inputs/outputs, step-by-step instructions, acceptance criteria, and review checklist.

## Conventions
- Language: Python 3.10+
- Only standard library unless noted
- Use pathlib for paths; UTF-8 for I/O
- All tools must be read-only by default; mutating tools require `apply=true` and must support dry-run diffs
- Location structure: `{uri, start:{line,column}, end:{line,column}}` (0-based indices)

---

## 0. Project Scaffolding and Dev Tooling

### 0.1 Repository Scaffolding
- Goal: Create minimal project layout to host the MCP server and tools.
- Deliverables:
  - `src/mcp_pytools/` package with `__init__.py`
  - `src/mcp_pytools/server.py`
  - `src/mcp_pytools/tools/` package
  - `src/mcp_pytools/index/` package
  - `tests/` with placeholder tests
  - `pyproject.toml` (build-system, project metadata)
  - `README.md` (how to run)
- Steps:
  1) Create directories and files as above.
  2) In `pyproject.toml`, define build-system using `hatchling` or `setuptools`.
  3) Add minimal server entry point in `server.py` with stubbed routing.
- Acceptance:
  - `pytest -q` runs and finds at least one placeholder test.
- Review checklist: Structure matches; package imports succeed.

### 0.2 Coding Standards and CI
- Goal: Ensure consistent formatting and linting.
- Deliverables: `ruff.toml`, `pyproject.toml` black config, GitHub Actions (optional).
- Steps:
  1) Configure Black (line-length 100), Ruff (flake8 rules), isort profile black.
  2) Add pre-commit config (optional) with black, ruff, isort.
- Acceptance: `ruff .` and `black --check .` pass.

---

## 1. File System Layer and Ignoring Rules

### 1.1 Ignore Patterns
- Goal: Implement ignore handling similar to .gitignore.
- Deliverables: `src/mcp_pytools/fs/ignore.py`
- Steps:
  1) Implement loader that reads `.gitignore`, `.mcpignore` if present.
  2) Use `fnmatch` and directory-based pruning; cache compiled patterns.
  3) Provide `is_ignored(path: Path) -> bool` and `walk_python_files(root: Path) -> Iterator[Path]`.
- Acceptance: Unit tests simulate nested ignores; files excluded correctly.
- Review: Edge cases (negation !, leading slash, dir vs file) covered where feasible; document limitations.

### 1.2 File Cache
- Goal: Cache file contents and metadata.
- Deliverables: `src/mcp_pytools/fs/cache.py`
- Steps:
  1) Define `FileRecord` dataclass: path, mtime_ns, size, sha256.
  2) Implement `FileCache` with `get_text(path)`, `get_bytes(path)`, `stat(path)`, `invalidate(path)`.
  3) Compute hash lazily; verify freshness via mtime_ns.
- Acceptance: Tests modify files and verify cache invalidation.
- Review: Thread-safety via simple lock; Unicode errors handled.

---

## 2. AST Parsing and Augmented Model

### 2.1 Parse with Positions
- Goal: Parse Python into AST with parent links and node spans.
- Deliverables: `src/mcp_pytools/astutils/parser.py`
- Steps:
  1) Use `ast.parse(source, filename, type_comments=True)`.
  2) Build visitor to attach `_parent` and `_range` to nodes using `ast.get_source_segment` and `node.lineno/col_offset` plus `end_lineno/end_col_offset` (3.8+).
  3) Provide `parse_module(text, uri) -> ParsedModule` with fields: `tree`, `text`, `lines`, `uri`.
- Acceptance: Tests assert parents and ranges exist for key nodes.
- Review: Handles SyntaxError returning structured error with location.

### 2.2 Symbol Extraction
- Goal: Build per-module symbol table.
- Deliverables: `src/mcp_pytools/analysis/symbols.py`
- Steps:
  1) Visitor collects `ClassDef`, `FunctionDef/AsyncFunctionDef`, assignments to Name at module/class scope.
  2) Store `Symbol{name, kind, range, container}`; export `document_symbols(module) -> list[Symbol]`.
  3) Track `__all__` if simple list of strings.
- Acceptance: Tests on sample modules; ordering stable.
- Review: Nested defs tracked with container path (e.g., `Class.method`).

### 2.3 Import Graph
- Goal: Extract imports (edges) and build reverse map.
- Deliverables: `src/mcp_pytools/analysis/imports.py`
- Steps:
  1) Visit `Import` and `ImportFrom` to record edges with aliases.
  2) Normalize module names relative to package; infer module uri from file layout.
  3) Provide `import_edges(module) -> list[ImportEdge]` and `build_graph(all_modules)`.
- Acceptance: Tests on package with relative imports.
- Review: Star imports marked as `wildcard=True` and treated conservatively.

---

## 3. Project Indexer

### 3.1 Index Build
- Goal: Build in-memory index for project.
- Deliverables: `src/mcp_pytools/index/project.py`
- Steps:
  1) Scan python files via `walk_python_files`.
  2) Parse each file; store `ParsedModule` in cache.
  3) Build symbol tables, import graph; create maps:
     - `module_by_uri`
     - `defs_by_name` (qualified and unqualified)
     - `refs` placeholder for later
  4) Return stats `{files, parse_errors}`.
- Acceptance: Test small sample project; stats correct.
- Review: Gracefully records syntax errors without aborting.

### 3.2 Incremental Invalidation
- Goal: Update index efficiently on file change.
- Deliverables: Methods on `ProjectIndex` for `invalidate(uri)` and `rebuild(uri)`.
- Steps:
  1) Compare mtime/hash to detect change.
  2) Reparse file, update symbol table and affected graphs.
- Acceptance: Tests modify one file and confirm limited recomputation.
- Review: Thread-safe updates using locks.

---

## 4. Navigation Tools

### 4.1 Document Symbols Tool
- Goal: Expose outline per file.
- Deliverables: `tools/document_symbols.py` tool handler.
- Input: `{uri}`
- Output: `[Symbol]`
- Steps: Load from index; if missing, parse on demand.
- Acceptance: Returns ordered outline matching source.
- Review: Includes ranges and container names.

### 4.2 Find Definition
- Goal: Jump to definition from position.
- Deliverables: `tools/find_definition.py`
- Input: `{uri, position:{line,column}}`
- Output: `Location | null`
- Steps:
  1) Identify token at position (use tokenize).
  2) Resolve in local scopes, then imports (alias handling), then project-level defs.
  3) Return first-best location.
- Acceptance: Works for local vars, functions, imported names.
- Review: Conservative for dynamic attributes; returns null if unsure.

### 4.3 Find References
- Goal: Static reference search.
- Deliverables: `tools/find_references.py`
- Input: `{uri, position}` or `{symbol}`
- Output: `[Location]`
- Steps:
  1) Resolve target definition as in 4.2.
  2) Walk modules to find Name nodes matching and bound to target via scope analysis.
- Acceptance: Finds refs in same module and via imports when alias resolves.
- Review: Avoid false positives by respecting scope and alias maps.

### 4.4 Import Graph Tool
- Goal: Show direct imports and reverse deps.
- Deliverables: `tools/import_graph.py`
- Input: `{moduleUri}`
- Output: `{imports:[...], dependents:[...]}`
- Steps: Query index graphs.
- Acceptance: Matches analysis/imports edges.

### 4.5 Search Text
- Goal: Regex search with ignores.
- Deliverables: `tools/search_text.py`
- Input: `{pattern, includeGlobs?, excludeGlobs?}`
- Output: `[Match{uri, range, line}]`
- Steps: Iterate files, apply pattern with `re` and flags.
- Acceptance: Correct matches; respects ignores.

---

## 5. Quality and Diagnostics Tools

### 5.1 Docstring Lints
- Goal: Report missing/incomplete docstrings.
- Deliverables: `tools/docstring_lints.py`
- Steps: For each def/class/module, check first statement is `ast.Expr` with `ast.Constant(str)`.
- Output: `[Diagnostic{uri, range, message, severity}]`
- Acceptance: Flags missing docstrings; ignores private names `_` by option.

### 5.2 Mutable Default Args
- Goal: Flag mutable defaults.
- Deliverables: `tools/mutability_check.py`
- Steps: Inspect `FunctionDef.args.defaults` for `List`, `Dict`, `Set`, `Call` to constructors.
- Acceptance: Produces diagnostics with fix suggestion text.

### 5.3 Syntax Check
- Goal: Validate syntax quickly.
- Deliverables: `tools/syntax_check.py`
- Steps: Parse and return SyntaxError details if any.
- Acceptance: Correct error locations and messages.

---

## 6. Refactor Tools (Conservative, Dry-run First)

### 6.1 Organize Imports
- Goal: Sort, group, and remove unused imports.
- Deliverables: `tools/organize_imports.py`
- Steps:
  1) Analyze used names in module.
  2) Build new import blocks (stdlib vs third-party vs local groups).
  3) Generate unified diff; apply only if `apply=true`.
- Acceptance: Dry-run shows diff; applying updates file; tests verify idempotency.

### 6.2 Rename Symbol
- Goal: Rename def and all safe references.
- Deliverables: `tools/rename_symbol.py`
- Steps:
  1) Resolve definition.
  2) Collect references via 4.3.
  3) Validate new name (identifier, no conflicts in scope).
  4) Produce edits; dry-run then apply.
- Acceptance: Tests for local function, class method, and imported alias.

---

## 7. MCP Server Integration

### 7.1 Tool Interface and Routing
- Goal: Define a simple tool interface and dispatcher.
- Deliverables: `server.py`, `tools/__init__.py`
- Steps:
  1) Define Tool protocol: `name`, `schema`, `handle(request) -> result`.
  2) Register tools in a registry; auto-discover via module import.
  3) Add JSON-RPC-like loop (stdin/stdout) or framework you use for MCP.
- Acceptance: Server lists tools and executes one with sample input.

### 7.2 Project Index Lifecycle
- Goal: Manage index creation and refresh.
- Steps:
  1) On server start, build index for configured root.
  2) Add `index.build`, `index.status`, `index.invalidate` tools.
- Acceptance: Index stats returned; invalidate triggers partial rebuild.

### 7.3 Error Handling and Telemetry
- Goal: Robust failures with actionable messages.
- Steps:
  1) Wrap tool handlers; return structured errors `{code, message, data}`.
  2) Optional logging with timestamps and tool names.
- Acceptance: Fault injection tests produce clean errors.

---

## 8. Testing Strategy

### 8.1 Unit Tests
- For each module: parser, symbols, imports, search, tools.
- Use tiny fixture projects in `tests/fixtures/`.
- Acceptance: 90%+ path coverage on core analysis; avoid brittle string checks.

### 8.2 Golden Diff Tests
- For refactors, store expected unified diffs.
- Verify apply produces exact file contents.

### 8.3 Performance Smoke Tests
- Index a medium fixture (~200 files) within reasonable time (<3s on dev laptop; document actual).

---

## 9. Documentation

### 9.1 User Docs
- README sections: installing, running server, listing tools, example invocations.

### 9.2 Developer Docs
- CONTRIBUTING with local dev commands, testing, code layout.

---

## 10. Delivery Checklist
- All tools support `dryRun` where applicable.
- Inputs validated; schemas documented.
- Edge cases documented: star imports, dynamic attrs, syntax errors.
- Tests green; formatting and linting pass.
- Example scripts provided to demo core features.
