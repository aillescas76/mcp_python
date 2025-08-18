# MCP Server for Python Code Navigation — Plan

## Goals
- Provide an MCP server exposing tools to navigate, query, and transform Python code using only static analysis (no external services).
- Support file/project-level operations, symbol discovery, AST-based queries/edits, and safety checks.
- Keep it fast and robust using the standard library and well-known parsing libraries (primarily `ast`).

## Architecture
- Transport/protocol: MCP server (Node/Python host) with Python tool handlers.
- Code model:
  - File loader with caching and invalidation on mtime/hash.
  - Project indexer scanning Python files (configurable root, excludes via .gitignore-like patterns).
  - Symbol index built using `ast` + custom visitors; store cross-ref maps (definitions, references, imports).
  - Optional type info hooks (peeking at typing annotations, literal/structural types from AST, no runtime imports).
- Safety: Read-only by default; mutating tools require explicit flags and dry-run diffs.

## Data Structures
- FileGraph: files, imports (edges), reverse-import map.
- SymbolTable: module -> {classes, functions, variables, assignments} with spans.
- CrossRefs: definition -> references (file, range), import origins, aliasing.
- AST Cache: file -> parsed `ast.AST` + auxiliary maps (node->span, parent links).
- Text edits: unified diff format, or LSP-style TextEdit list.

## Tools to Implement (code-only)

### Navigation and Query
- project.list_files: List Python files with filters (glob, size, mtime).
- project.search_text: Fast regex search over files (with ignore patterns).
- project.search_symbols: Find symbols by name/pattern (func/class/var/module).
- project.find_definition: Given file+position or symbol, return definition location.
- project.find_references: Static reference search via AST + import resolution.
- project.find_implementations: Class method overrides/implementations (inheritance tree).
- project.document_symbols: Outline per file (classes, functions, assignments).
- project.call_hierarchy: Approximate call graph edges (function calls from AST).
- project.import_graph: Show imports of a module and reverse dependencies.

### AST and Structure
- ast.parse_file: Return AST summary (node kinds, spans).
- ast.query: Mini query language (e.g., `FunctionDef[name~="^test_"]`).
- ast.parents: Return parent chain for node at position.
- ast.dump_range: Dump AST at range (pretty-printed).
- ast.metrics: LOC, number of defs, complexity proxies (branches, nesting).

### Refactoring and Edits (static-safe)
- refactor.rename_symbol: Rename across project using def-use chains; dry-run diff.
- refactor.rename_parameter: Rename param and all call sites by keyword.
- refactor.extract_function: Extract selected range into new function; replace with call.
- refactor.inline_variable: Inline simple assigned names where safe.
- refactor.move_symbol: Move class/function between modules; rewrite imports.
- refactor.organize_imports: Group/sort/remove unused imports (AST-based).
- refactor.add_type_hints: Insert inferred or placeholder annotations (from AST context).
- refactor.convert_fstring/format: Transform string formatting styles.
- refactor.replace_deprecated: Pattern-based API replacements via rules.

### Code Intelligence
- intel.infer_types_light: Heuristic type inference from literals/returns/annotations.
- intel.unused_symbols: Detect unused imports/locals/private functions.
- intel.dead_code: Identify unreachable branches and never-called functions (static heuristic).
- intel.cyclomatic_complexity: Compute per-function complexity from AST.
- intel.api_surface: Extract public API (exports, __all__, leading underscore filtering).

### Quality and Safety
- qa.docstring_lints: Check missing/incomplete docstrings by kind.
- qa.mutability_check: Flag mutable defaults in function defs.
- qa.exception_paths: List bare excepts, broad exceptions, re-raise correctness.
- qa.shadowing_check: Name shadowing (builtins, outer scopes).
- qa.side_effects_in_top_level: Detect top-level I/O/mutations (import-time side effects).

### Code Generation (structure-safe)
- gen.create_module: Scaffold module with classes/functions stubs.
- gen.add_dataclass: Convert simple class to `@dataclass` from assignments/init.
- gen.interface_from_class: Emit `Protocol` from class public methods.
- gen.test_skeletons: Create pytest skeletons for functions/classes discovered.

### Diagnostics and Utilities
- diag.tokenize: Return tokens at position/range (tokenize module).
- diag.syntax_check: Parse with `ast` to validate syntax and error location.
- diag.format_range: Reformat a range using custom minimal formatter (no external tools).
- utils.diff_preview: Produce unified diff for any proposed edits.
- utils.batch_apply_edits: Apply atomic multi-file edits; rollback on conflict.

### Project Indexing and Caching
- index.build: Build/rebuild indices; return stats (files, symbols).
- index.status: Cache stats, freshness, memory usage.
- index.invalidate: Invalidate file(s) or entire index.

## Implementation Plan (minimal to robust)

### Phase 1: Core and Read-only
1) Project scanning and file cache
- Walk project root, apply ignores, store file contents + hashes.
- Expose `project.list_files`, `project.search_text`.

2) AST parsing and symbol extraction
- Parse files with `ast.parse`; attach parent links and positions via `ast.NodeVisitor`.
- Build per-module SymbolTable; expose `document_symbols`, `ast.parse_file`, `ast.metrics`.

3) Basic navigation
- `find_definition`: Resolve names using scope rules and imports.
- `find_references`: Track Identifier -> definition map; use reverse index.
- `import_graph`: Build edges from Import/ImportFrom.

### Phase 2: Cross-file intelligence
4) Call graph and implementations
- `call_hierarchy`: Collect Call nodes and map potential targets.
- `find_implementations`: Build inheritance graph; method override mapping.

5) Quality checks
- Implement qa.* visitors (docstrings, exceptions, shadowing, mutable defaults, side effects).

### Phase 3: Safe refactors
6) Rename and organize imports
- `refactor.rename_symbol` with conflict detection, scope-aware.
- `refactor.organize_imports`: Merge duplicates, sort, remove unused.

7) Move symbol and inline/Extract
- `move_symbol`: Update imports/qualifiers; avoid new cycles.
- `inline_variable` and `extract_function` with conservative guards.

### Phase 4: Generation and typing aids
8) Type hints and dataclass conversion
- `add_type_hints`: Fill from literals/annotations; placeholders where unknown.
- `add_dataclass`: Detect `__init__`/attribute assigns; generate fields.

### Phase 5: Performance and robustness
9) Incremental indexing and invalidation
- Watch mtimes; only reparse changed files. Optional process pool for parsing.

10) Testing and safety
- Unit tests per tool; golden diffs for refactors. Dry-run default; require `apply=true` to write.

## Tool I/O Contracts (suggested)
- Locations: `{uri, start: {line, column}, end: {line, column}}`
- Symbols: `{name, kind, range, detail, containerName}`
- Edits: `[{uri, range, newText}]` or unified diff string
- Options: `{dryRun: boolean, include: globs[], exclude: globs[]}`

## Edge Cases to Handle
- Relative/absolute imports, aliasing (import x as y).
- Star imports (conservative handling or require allowlist).
- Dynamic attribute access, exec/eval (unsupported/flag).
- Generated code, vendored dirs, virtualenvs (exclude).
- Mixed encodings and invalid syntax (report and continue).
- Multi-assignments, destructuring, shadowing across scopes.

## Minimal Tech Stack
- Python stdlib: `ast`, `tokenize`, `token`, `pathlib`, `re`, `difflib`, `dataclasses`, `typing`.
- Optional: `libcst` for precise code mods (format-preserving). Prefer stdlib initially.

## Example Tool Set to Start (MVP)
- project.list_files
- project.search_text
- ast.parse_file
- document_symbols
- find_definition
- find_references
- import_graph
- refactor.organize_imports (dry-run only)
- qa.docstring_lints
- utils.diff_preview, utils.batch_apply_edits
